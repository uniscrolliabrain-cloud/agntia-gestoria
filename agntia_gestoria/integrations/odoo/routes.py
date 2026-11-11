import json
import uuid
from typing import Literal
from fastapi import APIRouter,Depends,Query,Request,HTTPException
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import Field
from ...auth import Actor,authenticate,company_access
from ...models import Model
from ...storage import canonical,digest,identifier,now
from ...tax import TaxRecord
from .. import policy
from ..contracts import ConnectionCreate,BindingValidation,Revision,PreviewRequest,ImportRequest,PartnerChange,DraftInvoiceRequest,ApprovalRequest,CommitRequest,Opaque,HexId
from ..errors import IntegrationError,reject
from ..migrations import migrate
from .adapter import Adapter
from .evidence import event


class PreviewJob(PreviewRequest):
    idempotency_key:Opaque


class Resolution(Model):
    revision:int=Field(ge=0)
    decision:Literal['keep_local','supersede_local']
    notes:str=Field(min_length=5,max_length=3000)


class ReconcileRequest(Model):
    idempotency_key:Opaque


class DocumentDownload(Model):
    attachment_id:int=Field(gt=0)


class Acknowledge(Model):
    event_ids:list[HexId]=Field(min_length=1,max_length=200)


class Classification(Model):
    revision:int=Field(ge=0)
    operation_date:str
    tax_kind:Literal['iva','igic','ipsi','none','other']
    category:Literal['ordinary','asset','payroll','rent','agricultural','other']
    vat_treatment:Literal['domestic_current','investment','intra_eu','import','cash','exempt','other']
    tax_rate:str|None=None
    deductible_tax_amount:str|None=None
    deductible_irpf_amount:str|None=None
    document_ids:list[HexId]=Field(min_length=1,max_length=100)
    notes:str=Field(min_length=5,max_length=3000)
    issued_evidence_confirmed:bool=False


def audit_failed_attempt(request,code,correlation_id):
    try:
        actor=authenticate(request);cid=request.path_params.get('cid','');company_access(actor,cid);identifier(cid)
        db=request.app.state.db
        with db.transaction() as c:
            db.company(c,cid);db.audit(c,cid,actor,'integration.attempt.failed',cid,{'code':code,'correlation_id':correlation_id})
    except Exception:pass


class IntegrationRoute(APIRoute):
    def get_route_handler(self):
        original=super().get_route_handler()
        async def handler(request):
            try:return await original(request)
            except RequestValidationError:
                audit_failed_attempt(request,'validation',str(uuid.uuid4()))
                return JSONResponse({'code':'validation','message':'Entrada inválida para la capacidad solicitada','correlation_id':str(uuid.uuid4()),'retryable':False,'reconciliation_required':False},status_code=422)
            except HTTPException as exc:
                code={401:'auth',403:'forbidden',404:'not_found'}.get(exc.status_code,'validation')
                audit_failed_attempt(request,code,str(uuid.uuid4()))
                return JSONResponse({'code':code,'message':{401:'Autenticación necesaria',403:'Operación no autorizada',404:'Recurso no encontrado'}.get(exc.status_code,'Solicitud inválida'),'correlation_id':str(uuid.uuid4()),'retryable':False,'reconciliation_required':False},status_code=exc.status_code)
            except ValueError:
                audit_failed_attempt(request,'validation',str(uuid.uuid4()))
                return JSONResponse({'code':'validation','message':'Datos o identificadores inválidos','correlation_id':str(uuid.uuid4()),'retryable':False,'reconciliation_required':False},status_code=422)
        return handler


def register_odoo_routes(app,db):
    if policy.enabled():migrate(db)
    router=APIRouter(prefix='/api/companies/{cid}/integrations/odoo',route_class=IntegrationRoute)
    def service(request:Request):
        # A typed injection point for tests, never a request-supplied provider URL/transport.
        return Adapter(db,getattr(app.state,'odoo_client_factory',None))
    def correlation(request):
        incoming=request.headers.get('X-Correlation-ID','')
        try:return str(uuid.UUID(incoming))
        except (ValueError,AttributeError):return str(uuid.uuid4())

    @app.exception_handler(IntegrationError)
    async def integration_error(request:Request,exc:IntegrationError):
        corr=correlation(request)
        # Record denied/failing mutation attempts without storing URL parameters or body/credentials.
        if request.method in ('POST','PUT','DELETE'):
            try:
                actor=authenticate(request);cid=request.path_params.get('cid','');company_access(actor,cid);identifier(cid)
                with db.transaction() as c:
                    db.company(c,cid);db.audit(c,cid,actor,'integration.attempt.failed',cid,{'code':exc.code,'correlation_id':corr})
            except Exception:pass
        return JSONResponse(exc.public(corr),status_code=exc.status)

    @router.post('/connections')
    def connect(cid:str,body:ConnectionCreate,request:Request,actor:Actor=Depends(authenticate)):return service(request).create_connection(actor,cid,body,correlation(request))
    @router.post('/connections/validate')
    def validate(cid:str,body:BindingValidation,request:Request,actor:Actor=Depends(authenticate)):return service(request).validate(actor,cid,body,correlation(request))
    @router.post('/connections/disable')
    def disable(cid:str,body:Revision,request:Request,actor:Actor=Depends(authenticate)):return service(request).disable(actor,cid,body.revision,correlation(request))
    @router.get('/health')
    @router.get('/capabilities')
    def health(cid:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).capabilities(actor,cid)
    @router.post('/imports/preview',status_code=202)
    def preview(cid:str,body:PreviewJob,request:Request,actor:Actor=Depends(authenticate)):return service(request).enqueue(actor,cid,'preview',body.model_dump(mode='json',exclude={'idempotency_key'}),body.idempotency_key,correlation(request))
    @router.post('/imports',status_code=202)
    def import_data(cid:str,body:ImportRequest,request:Request,actor:Actor=Depends(authenticate)):return service(request).enqueue(actor,cid,'import',{'staging_ids':body.staging_ids},body.idempotency_key,correlation(request))
    @router.get('/jobs/{job_id}')
    def job(cid:str,job_id:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).job(actor,cid,job_id)
    @router.get('/staging')
    def stages(cid:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).list_scoped(actor,cid,'integration_staging','imports.run')
    @router.get('/conflicts')
    def conflicts(cid:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).list_scoped(actor,cid,'integration_conflicts','conflicts.read')
    @router.post('/conflicts/{conflict_id}/resolve')
    def resolve(cid:str,conflict_id:str,body:Resolution,request:Request,actor:Actor=Depends(authenticate)):return service(request).resolve_conflict(actor,cid,conflict_id,body.revision,body.decision,body.notes,correlation(request))
    @router.get('/invoice-drafts/{draft_id}/projection-input')
    def projection(cid:str,draft_id:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).projection_input(actor,cid,draft_id)
    @router.post('/partners/dry-run')
    def partner(cid:str,body:PartnerChange,request:Request,actor:Actor=Depends(authenticate)):return service(request).propose_partner(actor,cid,body,correlation(request))
    @router.post('/invoice-drafts/dry-run')
    def invoice(cid:str,body:DraftInvoiceRequest,request:Request,actor:Actor=Depends(authenticate)):return service(request).propose_invoice(actor,cid,body,correlation(request))
    @router.post('/proposals/{proposal_id}/approve')
    def approve(cid:str,proposal_id:str,body:ApprovalRequest,request:Request,actor:Actor=Depends(authenticate)):return service(request).approve(actor,cid,proposal_id,body,correlation(request))
    @router.post('/partners/commit')
    @router.post('/invoice-drafts/commit')
    def commit(cid:str,body:CommitRequest,request:Request,actor:Actor=Depends(authenticate)):
        adapter=service(request);connection,_=adapter.scope(actor,cid,'writes.commit')
        with db.connection() as c:proposal=adapter._get_proposal(c,cid,connection['id'],body.proposal_id)
        expected='partner' if request.url.path.endswith('/partners/commit') else 'invoice_draft'
        if proposal['payload']['kind']!=expected:reject('validation','Tipo de propuesta incompatible con la capacidad',422)
        return adapter.commit_write(actor,cid,body,correlation(request))
    @router.post('/writes/reconcile')
    def reconcile(cid:str,body:ReconcileRequest,request:Request,actor:Actor=Depends(authenticate)):return service(request).reconcile_write(actor,cid,body.idempotency_key,correlation(request))
    @router.get('/invoices/{invoice_id}/attachments')
    def attachments(cid:str,invoice_id:int,request:Request,actor:Actor=Depends(authenticate)):return service(request).attachment_metadata(actor,cid,invoice_id)
    @router.post('/invoices/{invoice_id}/attachments/download')
    def download(cid:str,invoice_id:int,body:DocumentDownload,request:Request,actor:Actor=Depends(authenticate)):return service(request).download_attachment(actor,cid,invoice_id,body.attachment_id,correlation(request))
    @router.post('/records/{record_id}/classification')
    def classify(cid:str,record_id:str,body:Classification,request:Request,actor:Actor=Depends(authenticate)):
        adapter=service(request);connection,_=adapter.scope(actor,cid,'records.classify')
        with db.transaction() as c:
            record=db.get(c,cid,record_id,'tax_record')
            if record.get('provenance',{}).get('connection_id')!=connection['id']:reject('not_found','Registro de integración no encontrado',404)
            if record['status']=='void' or record['revision']!=body.revision:reject('conflict','Revisión o estado incorrectos',409)
            if record.get('provenance',{}).get('source_state')=='draft' and not body.issued_evidence_confirmed:reject('evidence_required','El borrador ERP no acredita emisión; confirma evidencia fiscal suficiente',422)
            for did in body.document_ids:db.get(c,cid,did,'document')
            original={**record};updated={k:record[k] for k in TaxRecord.model_fields if k in record}
            updated.update(body.model_dump(exclude={'revision','notes','issued_evidence_confirmed'}));updated['classification_notes']=body.notes
            validated=TaxRecord.model_validate(updated)
            db.put(c,cid,'integration_record_history',{'id':uid_for_history(),'company_id':cid,'record_id':record_id,'snapshot':original})
            record.update(validated.model_dump(mode='json'));record.update(status='unverified',revision=record['revision']+1,review=None,classification_actor=actor.id,fiscal_evidence_confirmation=body.issued_evidence_confirmed)
            db.put(c,cid,'tax_record',record);db.audit(c,cid,actor,'integration.record.classified',record_id,record)
        return record
    @router.get('/audit-integrity')
    def integrity(cid:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).audit_integrity(actor,cid)
    @router.get('/metrics')
    def metrics(cid:str,request:Request,actor:Actor=Depends(authenticate)):return service(request).metrics(actor,cid)
    @router.get('/events')
    def events(cid:str,request:Request,actor:Actor=Depends(authenticate)):
        adapter=service(request);connection,_=adapter.scope(actor,cid,'events.read',ready=False)
        with db.connection() as c:return [json.loads(row['body']) for row in c.execute("SELECT body FROM integration_outbox WHERE company_id=? AND connection_id=? AND state='pending' ORDER BY rowid LIMIT 500",(cid,connection['id']))]
    @router.post('/events/ack')
    def acknowledge(cid:str,body:Acknowledge,request:Request,actor:Actor=Depends(authenticate)):
        adapter=service(request);connection,_=adapter.scope(actor,cid,'events.ack',ready=False)
        from ...storage import uid
        with db.transaction() as c:
            for eid in body.event_ids:
                row=c.execute('SELECT 1 FROM integration_outbox WHERE id=? AND company_id=? AND connection_id=?',(eid,cid,connection['id'])).fetchone()
                if not row:reject('not_found','Evento no encontrado',404)
                prior=c.execute("SELECT 1 FROM integration_inbox WHERE company_id=? AND json_extract(body,'$.event_id')=? AND json_extract(body,'$.consumer_id')=?",(cid,eid,actor.id)).fetchone()
                if prior:continue
                ack={'event_id':eid,'consumer_id':actor.id,'at':now()};c.execute('INSERT INTO integration_inbox VALUES(?,?,?,?)',(uid(),cid,connection['id'],canonical(ack)))
                c.execute('UPDATE integration_outbox SET state=? WHERE id=?',('delivered',eid));db.audit(c,cid,actor,'integration.event.acked',eid,ack)
        return {'acknowledged':len(body.event_ids)}
    @router.get('/briefing')
    def briefing(cid:str,request:Request,actor:Actor=Depends(authenticate)):
        adapter=service(request);connection,_=adapter.scope(actor,cid,'health',ready=False)
        with db.connection() as c:
            conflicts=c.execute("SELECT count(*) FROM integration_conflicts WHERE company_id=? AND state='open'",(cid,)).fetchone()[0]
            documents=c.execute("SELECT count(*) FROM objects WHERE company_id=? AND kind='tax_record' AND json_extract(body,'$.provenance.connection_id')=? AND json_extract(body,'$.status')='unverified'",(cid,connection['id'])).fetchone()[0]
            jobs=[json.loads(r['body']) for r in c.execute('SELECT body FROM sync_jobs WHERE company_id=? ORDER BY rowid DESC LIMIT 10',(cid,))]
        return {'company_id':cid,'connection':adapter.public(connection),'open_conflicts':conflicts,'unreviewed_records':documents,'recent_jobs':[{'job_id':j['id'],'state':j['state'],'completed_at':j.get('completed_at')} for j in jobs],'source':'local persisted integration evidence','notice':'Laia puede resumir estos hechos; no acredita actividades, aprobaciones ni presentaciones no registradas.'}
    app.include_router(router)


def uid_for_history():
    from ...storage import uid
    return uid()
