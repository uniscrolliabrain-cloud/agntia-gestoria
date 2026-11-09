import hashlib
import json
import os
import re
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from . import __version__
from .auth import Actor, actors, authenticate, company_access, require_role
from .models import CaseCreate, CaseEdit, CompanyCreate, CompanyEdit, InvoiceDraft, JournalDraft, Model, Review, Revision, invoice_totals
from .rules import catalogue, evaluate
from .storage import Database, canonical, digest, identifier, now, uid
from .tax import register_tax_routes
from .report_routes import register_report_routes

load_dotenv()
WRITE = ('owner','reviewer','agent')
REVIEW = ('owner','reviewer')


def conflict(actual, expected):
    if actual != expected:
        raise HTTPException(409, 'El expediente ha cambiado. Lee su versión actual antes de editar.')


def case_content(case):
    return {key: case[key] for key in ('title','category','description','due_date','source_ids','document_ids')}


def calendar_export(cases):
    def escape(text):
        return str(text).replace('\\','\\\\').replace('\r','').replace('\n','\\n').replace(';','\\;').replace(',','\\,')
    result = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Agntia//Gestoria//ES','CALSCALE:GREGORIAN']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    for case in cases:
        if not case['due_date']:
            continue
        day = date.fromisoformat(case['due_date'])
        result.extend(['BEGIN:VEVENT',f"UID:{case['id']}@agntia-gestoria",f'DTSTAMP:{stamp}',f'DTSTART;VALUE=DATE:{day:%Y%m%d}',f'DTEND;VALUE=DATE:{day+timedelta(days=1):%Y%m%d}',
                       'SUMMARY:'+escape(('BORRADOR: ' if case['status'] not in ('reviewed','done') else '')+case['title']),
                       'DESCRIPTION:'+escape('Agenda interna; confirmar vencimiento y calendario oficial. No acredita presentación.\n'+case['description']), 'END:VEVENT'])
    result.append('END:VCALENDAR')
    # RFC 5545 folding by UTF-8 bytes, never splitting an encoded character.
    folded=[]
    for line in result:
        current=''
        for char in line:
            if len((current+char).encode())>73:
                folded.append(current);current=' '+char
            else: current+=char
        folded.append(current)
    return '\r\n'.join(folded)+'\r\n'


def create_app(data_dir=None):
    app = FastAPI(title='Agntia-gestoria', version=__version__, docs_url=None, redoc_url=None, openapi_url=None)
    db = Database(data_dir or os.getenv('GESTORIA_DATA_DIR','./data'))
    app.state.db = db
    # Fail early on malformed permission configuration; never fall back to anonymous access.
    actors()

    @app.middleware('http')
    async def same_origin(request, call_next):
        origin = request.headers.get('origin')
        if request.method not in ('GET','HEAD','OPTIONS') and origin and origin != str(request.base_url).rstrip('/'):
            return JSONResponse({'detail':'Origen no permitido'}, status_code=403)
        response = await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        return response

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({'detail':str(exc)},status_code=400)

    @app.exception_handler(FileNotFoundError)
    async def missing(request, exc):
        return JSONResponse({'detail':'Recurso no encontrado'},status_code=404)

    def access(connection, cid, actor):
        identifier(cid);company_access(actor,cid)
        return db.company(connection,cid)

    def references(connection,cid,data):
        known={item['id'] for item in catalogue()['sources']}
        if set(data.source_ids)-known:
            raise ValueError('Hay referencias normativas desconocidas')
        for doc in data.document_ids:
            db.get(connection,cid,doc,'document')

    @app.get('/api/status')
    def status(actor:Actor=Depends(authenticate)):
        return {'version':__version__,'actor':{'id':actor.id,'role':actor.role,'companies':list(actor.companies)},'external_submissions':False,'invoice_issuance':False,'pack_id':catalogue()['pack_id']}

    class Login(Model):
        token:str=Field(min_length=16,max_length=1000)

    @app.post('/api/login')
    def login(body:Login,request:Request):
        import hmac
        actor=next((a for secret,a in actors() if hmac.compare_digest(secret.encode(),body.token.encode())),None)
        if not actor: raise HTTPException(401,'Credencial incorrecta')
        response=JSONResponse({'actor_id':actor.id,'role':actor.role})
        response.set_cookie('gestoria_session',body.token,httponly=True,secure=request.url.scheme=='https',samesite='strict',max_age=28800)
        return response

    @app.post('/api/logout')
    def logout(actor:Actor=Depends(authenticate)):
        response=JSONResponse({'ok':True});response.delete_cookie('gestoria_session');return response

    @app.get('/api/openapi.json')
    def openapi(actor:Actor=Depends(authenticate)):return app.openapi()

    @app.get('/api/sources')
    def sources(actor:Actor=Depends(authenticate)):return catalogue()

    @app.get('/api/companies')
    def companies(actor:Actor=Depends(authenticate)):
        with db.connection() as connection:
            return [json.loads(row['body']) for row in connection.execute('SELECT id,body FROM companies ORDER BY rowid DESC') if actor.can_access(row['id'])]

    @app.post('/api/companies')
    def create_company(body:CompanyCreate,actor:Actor=Depends(authenticate)):
        require_role(actor,'owner')
        company={'id':uid(),'revision':0,**body.model_dump(mode='json'),'created_at':now()}
        with db.transaction() as connection:
            connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',(company['id'],canonical(company)))
            db.audit(connection,company['id'],actor,'company.created',company['id'],company)
        return company

    @app.get('/api/companies/{cid}')
    def company(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:return access(connection,cid,actor)

    @app.put('/api/companies/{cid}')
    def edit_company(cid:str,body:CompanyEdit,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            current=access(connection,cid,actor);conflict(current['revision'],body.revision)
            current.update(body.model_dump(mode='json',exclude={'revision'}));current['revision']+=1
            connection.execute('UPDATE companies SET body=? WHERE id=?',(canonical(current),cid))
            db.audit(connection,cid,actor,'company.updated',cid,current)
        return current

    @app.get('/api/companies/{cid}/obligations')
    def obligations(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:return evaluate(access(connection,cid,actor))

    @app.get('/api/companies/{cid}/cases')
    def cases(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:
            access(connection,cid,actor);return db.list(connection,cid,'case')

    @app.post('/api/companies/{cid}/cases')
    def new_case(cid:str,body:CaseCreate,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            access(connection,cid,actor);references(connection,cid,body)
            case={'id':uid(),'company_id':cid,'revision':0,'status':'draft','created_at':now(),'created_by':actor.id,'review':None,**body.model_dump(mode='json')}
            db.put(connection,cid,'case',case);db.audit(connection,cid,actor,'case.created',case['id'],case)
        return case

    @app.post('/api/companies/{cid}/generate-plan')
    def generate_plan(cid:str,body:Revision,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        created=[];existing=[]
        with db.transaction() as connection:
            company=access(connection,cid,actor);conflict(company['revision'],body.revision);plan=evaluate(company)
            for item in plan['obligations']:
                if item['applicability'] not in ('applies','needs_facts'):continue
                key=f"{plan['pack_id']}:{item['rule_id']}:{company['facts'].get('fiscal_year_end') or 'unconfirmed-period'}"
                found=connection.execute('SELECT id FROM objects WHERE company_id=? AND unique_key=?',(cid,key)).fetchone()
                if found:existing.append(found['id']);continue
                case={'id':uid(),'company_id':cid,'revision':0,'status':'draft','created_at':now(),'created_by':actor.id,'review':None,
                    'title':('Confirmar: ' if item['applicability']=='needs_facts' else '')+item['title'],'category':item['category'],
                    'description':item['explanation']+'\nPropuesta del paquete '+plan['pack_id']+'. '+('Faltan datos: '+', '.join(item['missing_facts']) if item['missing_facts'] else '')+'\nToda fecha es nominal hasta su revisión.',
                    'due_date':item['due_date'],'source_ids':item['source_ids'],'document_ids':[],'proposal':item,'company_revision':company['revision'],'pack_digest':plan['pack_digest']}
                db.put(connection,cid,'case',case,key);db.audit(connection,cid,actor,'case.proposed',case['id'],case);created.append(case['id'])
        return {'created':created,'existing':existing,'pack_stale':plan['pack_stale'],'notice':'Los expedientes existentes no se sobrescriben al regenerar.'}

    @app.get('/api/companies/{cid}/cases/{oid}')
    def get_case(cid:str,oid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);return db.get(connection,cid,oid,'case')

    @app.put('/api/companies/{cid}/cases/{oid}')
    def edit_case(cid:str,oid:str,body:CaseEdit,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            access(connection,cid,actor);case=db.get(connection,cid,oid,'case');conflict(case['revision'],body.revision);references(connection,cid,body)
            if case['status']=='done':raise HTTPException(409,'El expediente cerrado es de consulta; crea otro para la rectificación')
            case.update(body.model_dump(mode='json',exclude={'revision'}));case.update(revision=case['revision']+1,status='draft',review=None)
            db.put(connection,cid,'case',case);db.audit(connection,cid,actor,'case.updated',oid,case)
        return case

    @app.post('/api/companies/{cid}/cases/{oid}/submit-review')
    def submit_review(cid:str,oid:str,body:Revision,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            access(connection,cid,actor);case=db.get(connection,cid,oid,'case');conflict(case['revision'],body.revision)
            if case['status']!='draft':raise HTTPException(409,'Solo se envían borradores a revisión')
            case.update(status='in_review',revision=case['revision']+1)
            db.put(connection,cid,'case',case);db.audit(connection,cid,actor,'case.submitted_for_review',oid,case)
        return case

    @app.post('/api/companies/{cid}/cases/{oid}/review')
    def review_case(cid:str,oid:str,body:Review,actor:Actor=Depends(authenticate)):
        require_role(actor,*REVIEW)
        with db.transaction() as connection:
            access(connection,cid,actor);case=db.get(connection,cid,oid,'case');conflict(case['revision'],body.revision)
            if case['status']!='in_review':raise HTTPException(409,'El expediente no está pendiente de revisión')
            if body.decision=='approve' and set(body.verified_source_ids)!=set(case['source_ids']):raise ValueError('Confirma todas las fuentes del expediente al aprobar')
            case['revision']+=1;case['status']='reviewed' if body.decision=='approve' else 'draft'
            case['review']={'actor_id':actor.id,'at':now(),'notes':body.notes,'decision':body.decision,'verified_source_ids':body.verified_source_ids,'content_hash':digest(case_content(case)),'reviewed_revision':case['revision'],'meaning':'Revisión interna; no acredita presentación ni certificación legal.'}
            db.put(connection,cid,'case',case);db.audit(connection,cid,actor,'case.reviewed',oid,case)
        return case

    @app.post('/api/companies/{cid}/cases/{oid}/close')
    def close_case(cid:str,oid:str,body:Revision,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            access(connection,cid,actor);case=db.get(connection,cid,oid,'case');conflict(case['revision'],body.revision)
            if case['status']!='reviewed' or not case.get('review') or case['review']['content_hash']!=digest(case_content(case)):raise HTTPException(409,'Requiere revisión vigente del contenido actual')
            case.update(status='done',revision=case['revision']+1,closed_at=now(),outcome='internal_complete')
            db.put(connection,cid,'case',case);db.audit(connection,cid,actor,'case.closed_internally',oid,case)
        return case

    @app.post('/api/companies/{cid}/documents')
    def upload(cid:str,file:UploadFile=File(...),actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.connection() as connection:access(connection,cid,actor)
        name=(file.filename or 'documento').replace('\\','/').split('/')[-1][:200];suffix=Path(name).suffix.lower()
        if suffix not in ('.pdf','.png','.jpg','.jpeg','.csv','.txt'):raise ValueError('Admite PDF, PNG, JPG, CSV y TXT')
        did=uid();folder=db.root/'documents'/identifier(cid);folder.mkdir(parents=True,exist_ok=True);target=folder/(did+suffix)
        limit=float(os.getenv('GESTORIA_MAX_UPLOAD_MB','20'))*1024**2
        try:
            size=0;hashed=hashlib.sha256();head=b''
            with target.open('wb') as handle:
                while chunk:=file.file.read(1024*1024):
                    size+=len(chunk)
                    if size>limit:raise ValueError('Documento demasiado grande')
                    if not head:head=chunk[:16]
                    hashed.update(chunk);handle.write(chunk)
            if size==0:raise ValueError('Documento vacío')
            if suffix=='.pdf' and not head.startswith(b'%PDF-'):raise ValueError('Cabecera PDF inválida')
            if suffix=='.png' and not head.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Cabecera PNG inválida')
            if suffix in ('.jpg','.jpeg') and not head.startswith(b'\xff\xd8\xff'):raise ValueError('Cabecera JPEG inválida')
            if suffix in ('.csv','.txt'):
                raw=target.read_bytes();raw.decode('utf-8-sig')
                if b'\x00' in raw:raise ValueError('El documento de texto contiene bytes nulos')
            document={'id':did,'company_id':cid,'name':name,'stored_name':target.name,'size':size,'sha256':hashed.hexdigest(),'created_at':now(),'created_by':actor.id,'content_untrusted':True,'status':'original_unverified'}
            with db.transaction() as connection:
                access(connection,cid,actor);db.put(connection,cid,'document',document);db.audit(connection,cid,actor,'document.stored',did,document)
            return document
        except Exception:
            target.unlink(missing_ok=True);raise
        finally:file.file.close()

    @app.get('/api/companies/{cid}/documents')
    def documents(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);return db.list(connection,cid,'document')

    @app.get('/api/companies/{cid}/documents/{oid}/download')
    def download(cid:str,oid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);doc=db.get(connection,cid,oid,'document')
        return FileResponse(db.root/'documents'/cid/doc['stored_name'],filename=doc['name'],media_type='application/octet-stream')

    @app.post('/api/companies/{cid}/invoice-drafts')
    def invoice(cid:str,body:InvoiceDraft,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            company=access(connection,cid,actor)
            draft={'id':uid(),'company_id':cid,'status':'draft_not_issued','created_by':actor.id,'created_at':now(),**body.model_dump(mode='json'),'totals':invoice_totals(body),
                   'notice':'BORRADOR ECONÓMICO. No es una factura emitida, no asigna número fiscal y no genera registros SIF ni factura electrónica.',
                   'source_ids':['invoicing','vat','irpf'],'warnings':[]}
            if not company['nif'] or not company['address'] or not body.customer_nif or not body.customer_address:draft['warnings'].append('Faltan datos identificativos para revisar una eventual factura completa.')
            if (company['tax_territory']=='canarias' and body.tax_kind=='iva') or (company['tax_territory']=='common' and body.tax_kind=='igic'):draft['warnings'].append('Impuesto y territorio requieren revisión por operación; no se valida automáticamente la localización.')
            draft['warnings'].append('Los tipos y retenciones son datos introducidos por el usuario; el programa no determina su corrección jurídica.')
            db.put(connection,cid,'invoice_draft',draft);db.audit(connection,cid,actor,'invoice_draft.created',draft['id'],draft)
        return draft

    @app.get('/api/companies/{cid}/invoice-drafts')
    def invoices(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);return db.list(connection,cid,'invoice_draft')

    @app.post('/api/companies/{cid}/journal-drafts')
    def journal(cid:str,body:JournalDraft,actor:Actor=Depends(authenticate)):
        require_role(actor,*WRITE)
        with db.transaction() as connection:
            access(connection,cid,actor)
            for did in body.document_ids:db.get(connection,cid,did,'document')
            draft={'id':uid(),'company_id':cid,'status':'draft_not_posted','created_at':now(),'created_by':actor.id,**body.model_dump(mode='json'),'source_ids':['pgc','pgc-pymes'],'notice':'Borrador cuadrado, no asiento validado ni libro oficial.'}
            db.put(connection,cid,'journal_draft',draft);db.audit(connection,cid,actor,'journal_draft.created',draft['id'],draft)
        return draft

    @app.get('/api/companies/{cid}/journal-drafts')
    def journals(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);return db.list(connection,cid,'journal_draft')

    @app.get('/api/companies/{cid}/audit')
    def audit(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);return db.audit_log(connection,cid)

    @app.get('/api/companies/{cid}/calendar.ics')
    def calendar(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:access(connection,cid,actor);text=calendar_export(db.list(connection,cid,'case'))
        return Response(text,media_type='text/calendar',headers={'Content-Disposition':'attachment; filename="agenda-interna.ics"'})

    @app.get('/api/companies/{cid}/export')
    def export(cid:str,actor:Actor=Depends(authenticate)):
        with db.connection() as connection:
            company=access(connection,cid,actor)
            result={'company':company,'sources':catalogue(),'obligations':evaluate(company),'cases':db.list(connection,cid,'case'),'documents':db.list(connection,cid,'document'),
                    'tax_calculations':db.list(connection,cid,'tax_calculation'),'reports':db.list(connection,cid,'report'),'tax_records':db.list(connection,cid,'tax_record'),'tax_preparations':db.list(connection,cid,'tax_preparation'),'invoice_drafts':db.list(connection,cid,'invoice_draft'),'journal_drafts':db.list(connection,cid,'journal_draft'),'audit':db.audit_log(connection,cid),'exported_at':now(),'external_submissions':False}
        return JSONResponse(result,headers={'Content-Disposition':'attachment; filename="expediente-empresa.json"'})

    register_tax_routes(app,db)
    register_report_routes(app,db)
    app.mount('/',StaticFiles(directory=Path(__file__).parent/'static',html=True),name='workspace')
    return app
