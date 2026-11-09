import json
import hashlib
import hmac
import os
import time
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from ...storage import canonical,digest,identifier,now,uid
from ..errors import IntegrationError,reject
from .evidence import event


class Commands:
    def propose_partner(self,actor,cid,body,correlation):
        connection,server=self.scope(actor,cid,'partners.propose');self.require_capability(connection,'partners.write')
        if body.remote_id and body.remote_id not in server.allowed_partner_ids:reject('forbidden','Contacto fuera de la lista de escritura autorizada',403)
        client=self.client(actor,cid,'partners.propose',connection);before=None
        if body.remote_id:
            rows=client.call('res.partner','search_read',{'domain':[['id','=',body.remote_id],['company_id','=',server.odoo_company_id]],'fields':['id','name','vat','email','is_company','company_id','write_date'],'limit':1})
            if not isinstance(rows,list) or len(rows)!=1:reject('not_found','Contacto no accesible',404)
            before=rows[0]
            if before.get('write_date')!=body.expected_remote_write_date:reject('conflict','Contacto modificado en Odoo',409)
        payload={'kind':'partner','remote_id':body.remote_id,'expected_write_date':body.expected_remote_write_date,'values':body.model_dump(mode='json',exclude={'remote_id','expected_remote_write_date'})}
        return self._proposal(actor,cid,connection,payload,{'before_hash':digest(before),'fields_changed':list(payload['values'])},None,correlation)

    def projection_input(self,actor,cid,draft_id):
        self.scope(actor,cid,'invoices.read',ready=False)
        with self.db.connection() as c:draft=self.db.get(c,cid,draft_id,'invoice_draft')
        return {'invoice_draft_id':draft['id'],'source_hash':digest(draft),'totals':draft['totals'],'status':draft['status']}

    def propose_invoice(self,actor,cid,body,correlation):
        connection,server=self.scope(actor,cid,'invoices.propose');self.require_capability(connection,'invoice_drafts.write')
        if body.partner_id not in server.allowed_partner_ids or body.journal_id not in server.allowed_journal_ids or body.account_id not in server.allowed_account_ids or any(t not in server.allowed_tax_ids for t in body.tax_ids):reject('forbidden','Diario, contacto, cuenta o impuestos no autorizados',403)
        with self.db.connection() as c:
            draft=self.db.get(c,cid,body.invoice_draft_id,'invoice_draft')
            if c.execute('SELECT 1 FROM external_links WHERE company_id=? AND local_kind=? AND local_id=?',(cid,'invoice_draft',draft['id'])).fetchone():reject('conflict','Este borrador ya está proyectado; revisar el enlace existente',409)
        if digest(draft)!=body.expected_draft_hash:reject('conflict','El borrador local cambió',409)
        if Decimal(draft['withholding_rate'])!=0 or draft['tax_kind'] not in ('iva','igic','ipsi','none'):reject('unsupported','La proyección inicial no admite retenciones ni impuestos ambiguos',422)
        if len(body.tax_ids)>1:reject('unsupported','La proyección inicial no admite impuestos compuestos',422)
        for line in draft['lines']:
            if body.tax_ids:
                mapping=server.tax_mappings.get(str(body.tax_ids[0]),{})
                if mapping.get('tax_kind')!=draft['tax_kind'] or Decimal(str(mapping.get('rate','-1')))!=Decimal(line['tax_rate']):reject('conflict','El impuesto aprobado no corresponde al borrador local',409)
            elif Decimal(line['tax_rate'])!=0 or draft['tax_kind']!='none':reject('conflict','Falta un impuesto aprobado',409)
        payload={'kind':'invoice_draft','local_draft_id':draft['id'],'partner_id':body.partner_id,'journal_id':body.journal_id,'account_id':body.account_id,'tax_ids':body.tax_ids,'invoice_date':draft['operation_date'],'lines':[{'name':l['description'],'quantity':l['quantity'],'price_unit':l['unit_price']} for l in draft['lines']],'expected_totals':draft['totals'],'currency':'EUR'}
        quote=self.client(actor,cid,'invoices.propose',connection).call('agntia.bridge','preview_invoice',{'company_id':server.odoo_company_id,'payload':payload})
        for field in ('base','tax','total'):
            try:same=Decimal(quote[field])==Decimal(draft['totals'][field])
            except Exception:same=False
            if not same:reject('totals_mismatch','Los totales Odoo y Gestoría no coinciden; proyección bloqueada',409)
        return self._proposal(actor,cid,connection,payload,{'remote_totals':quote,'local_totals':draft['totals'],'remote_state':'draft','fiscal_issuance':False},digest(draft),correlation)

    def _proposal(self,actor,cid,connection,payload,diff,local_hash,correlation):
        proposal={'id':uid(),'company_id':cid,'connection_id':connection['id'],'tenant_id':connection['tenant_id'],'revision':0,'state':'proposed','created_by':actor.id,'created_at':now(),'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=15)).isoformat(),'connection_revision':connection['revision'],'payload':payload,'diff':diff,'local_source_hash':local_hash,'risk':'external_draft_or_contact_write','estimated_provider_fee':None,'notice':'Sin publicación, envío, pago ni presentación fiscal.'}
        proposal['proposal_hash']=digest(proposal)
        with self.db.transaction() as c:
            c.execute('INSERT INTO integration_proposals VALUES(?,?,?,?,?,?)',(proposal['id'],cid,connection['id'],0,'proposed',canonical(proposal)))
            event(self.db,c,connection,actor,'review.required',{'proposalId':proposal['id'],'proposalHash':proposal['proposal_hash']},correlation)
        return proposal

    def approve(self,actor,cid,proposal_id,body,correlation):
        connection,_=self.scope(actor,cid,'approvals.create')
        with self.db.transaction() as c:
            proposal=self._get_proposal(c,cid,connection['id'],proposal_id)
            if proposal['revision']!=body.revision or proposal['proposal_hash']!=body.proposal_hash or proposal['state']!='proposed':reject('conflict','Propuesta diferente o modificada',409)
            if datetime.fromisoformat(proposal['expires_at'])<datetime.now(timezone.utc):reject('expired','Propuesta caducada',409)
            approval={'id':uid(),'company_id':cid,'proposal_id':proposal_id,'proposal_hash':proposal['proposal_hash'],'actor_id':actor.id,'actor_role':actor.role,'at':now(),'expires_at':proposal['expires_at'],'notes':body.notes}
            c.execute('INSERT INTO integration_approvals VALUES(?,?,?,?)',(approval['id'],cid,proposal_id,canonical(approval)))
            event(self.db,c,connection,actor,'review.required',{'operation':'approved','approvalId':approval['id'],'proposalId':proposal_id},correlation)
        return approval

    @staticmethod
    def _get_proposal(c,cid,connection_id,proposal_id):
        row=c.execute('SELECT body FROM integration_proposals WHERE id=? AND company_id=? AND connection_id=?',(identifier(proposal_id),cid,connection_id)).fetchone()
        if not row:reject('not_found','Recurso no encontrado',404)
        proposal=json.loads(row['body']);proof=proposal.pop('proposal_hash')
        if digest(proposal)!=proof:reject('integrity','Integridad de propuesta inválida',409)
        proposal['proposal_hash']=proof
        return proposal

    def commit_write(self,actor,cid,body,correlation):
        connection,server=self.scope(actor,cid,'writes.commit')
        with self.db.transaction() as c:
            proposal=self._get_proposal(c,cid,connection['id'],body.proposal_id)
            requested_hash=digest({'proposal_id':body.proposal_id,'proposal_hash':proposal['proposal_hash']})
            old=c.execute('SELECT * FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation=? AND key=?',(cid,connection['id'],'write',body.idempotency_key)).fetchone()
            if old:
                if old['payload_hash']!=requested_hash:reject('idempotency_conflict','Clave ya vinculada a otra propuesta',409)
                return json.loads(old['body'])
            if c.execute("SELECT 1 FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation='write' AND json_extract(body,'$.proposal_id')=?",(cid,connection['id'],proposal['id'])).fetchone():reject('conflict','La propuesta ya tiene una ejecución; conciliar su clave original',409)
            if proposal['state']!='proposed' or proposal['revision']!=body.expected_revision or proposal['connection_revision']!=connection['revision']:reject('conflict','Propuesta o conexión modificadas',409)
            if datetime.fromisoformat(proposal['expires_at'])<datetime.now(timezone.utc):reject('expired','Propuesta caducada',409)
            row=c.execute('SELECT body FROM integration_approvals WHERE id=? AND company_id=? AND proposal_id=?',(identifier(body.approval_id),cid,proposal['id'])).fetchone()
            if not row:reject('approval_required','Aprobación humana necesaria',403)
            approval=json.loads(row['body'])
            if approval['proposal_hash']!=proposal['proposal_hash'] or approval['actor_role'] not in ('owner','reviewer') or datetime.fromisoformat(approval['expires_at'])<datetime.now(timezone.utc):reject('approval_required','Aprobación inválida o caducada',403)
            # A credential revoked after approval cannot authorize future effects.
            from ..policy import actor_for_job,authorize
            approver=actor_for_job(approval['actor_id']);authorize(approver,cid,connection['tenant_id'],'approvals.create')
            capability='partners.write' if proposal['payload']['kind']=='partner' else 'invoice_drafts.write';self.require_capability(connection,capability)
            if not server.write_enabled:reject('forbidden','Escritura desactivada',403)
            if proposal['payload']['kind']=='invoice_draft':
                draft=self.db.get(c,cid,proposal['payload']['local_draft_id'],'invoice_draft')
                if digest(draft)!=proposal['local_source_hash']:reject('conflict','El borrador local cambió después de aprobar',409)
                if c.execute('SELECT 1 FROM external_links WHERE company_id=? AND local_kind=? AND local_id=?',(cid,'invoice_draft',draft['id'])).fetchone():reject('conflict','Borrador ya proyectado',409)
            signing_key=os.getenv(server.approval_signing_key_env,'')
            if len(signing_key)<32:reject('not_configured','Firmante de aprobaciones no configurado',424)
            operation_key=digest({'tenant':connection['tenant_id'],'company':cid,'connection':connection['id'],'key':body.idempotency_key})
            intent={'status':'reconciliation_required','local_id':proposal['id'],'remote_id':None,'operation_key':operation_key,'proposal_id':proposal['id'],'proposal_hash':proposal['proposal_hash'],'approval_id':approval['id'],'payload_hash':digest(proposal['payload']),'reconciliation_required':True,'retryable':False}
            c.execute('INSERT INTO idempotency_keys VALUES(?,?,?,?,?,?,?)',(cid,connection['id'],'write',body.idempotency_key,requested_hash,'pending',canonical(intent)))
            event(self.db,c,connection,actor,'review.required',{'operation':'write_pending','proposalId':proposal['id'],'operationKey':operation_key},correlation)
        claims={'instance_id':server.expected_instance_id,'company_id':server.odoo_company_id,'operation_key':operation_key,'request_hash':intent['payload_hash'],'approval_id':approval['id'],'approved_by':approval['actor_id'],'expires_at':min(int(datetime.fromisoformat(approval['expires_at']).timestamp()),int(time.time())+300)}
        authorization={'claims':claims,'signature':hmac.new(signing_key.encode(),canonical(claims).encode(),hashlib.sha256).hexdigest()}
        try:
            result=self.client(actor,cid,'writes.commit',connection).call('agntia.bridge','execute_approved',{'company_id':server.odoo_company_id,'operation_key':operation_key,'request_hash':intent['payload_hash'],'payload':proposal['payload'],'authorization':authorization})
        except IntegrationError as exc:
            if exc.uncertain or exc.retryable:
                return self._uncertain(actor,cid,connection,body.idempotency_key,intent,exc.code,correlation)
            with self.db.transaction() as c:
                blocked={**intent,'status':'blocked','error':{'code':exc.code,'message':exc.message},'reconciliation_required':False}
                c.execute('UPDATE idempotency_keys SET state=?,body=? WHERE company_id=? AND connection_id=? AND operation=? AND key=?',('blocked',canonical(blocked),cid,connection['id'],'write',body.idempotency_key))
                event(self.db,c,connection,actor,'connection.degraded',{'code':exc.code,'proposalId':proposal['id']},correlation)
            raise
        return self._finish_write(actor,cid,connection,body.idempotency_key,intent,proposal,result,correlation)

    def _uncertain(self,actor,cid,connection,key,intent,code,correlation):
        result={**intent,'error':{'code':code,'message':'Resultado remoto pendiente de conciliación; no repetir create'}}
        with self.db.transaction() as c:
            if code in ('unsafe_remote_result','remote_totals_mismatch'):
                current=self._connection(c,cid,connection['id']);current.update(state='degraded',revision=current['revision']+1);self.save_connection(c,current)
            c.execute('UPDATE idempotency_keys SET state=?,body=? WHERE company_id=? AND connection_id=? AND operation=? AND key=?',('reconciliation_required',canonical(result),cid,connection['id'],'write',key))
            event(self.db,c,connection,actor,'connection.degraded',{'code':'write_uncertain','proposalId':intent['proposal_id']},correlation)
        return result

    def _finish_write(self,actor,cid,connection,key,intent,proposal,result,correlation):
        if not isinstance(result,dict) or result.get('request_hash')!=intent['payload_hash'] or type(result.get('remote_id'))!=int or result.get('company_id')!=connection['remote_company'] or result.get('kind')!=proposal['payload']['kind'] or (result['kind']=='invoice_draft' and result.get('state')!='draft'):
            return self._uncertain(actor,cid,connection,key,intent,'unsafe_remote_result',correlation)
        if result['kind']=='invoice_draft':
            try:matching=all(Decimal(result['totals'][k])==Decimal(proposal['payload']['expected_totals'][k]) for k in ('base','tax','total'))
            except Exception:matching=False
            if not matching:return self._uncertain(actor,cid,connection,key,intent,'remote_totals_mismatch',correlation)
        final={**intent,'status':'succeeded','remote_id':result['remote_id'],'remote_state':result.get('state'),'source_hash':digest(result),'reconciliation_required':False,'notice':'Contacto o borrador creado; no acredita emisión fiscal.'}
        with self.db.transaction() as c:
            old=c.execute('SELECT state,body FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation=? AND key=?',(cid,connection['id'],'write',key)).fetchone()
            if old['state']=='succeeded':return json.loads(old['body'])
            local_id=proposal['payload'].get('local_draft_id') or proposal['id'];kind='invoice_draft' if result['kind']=='invoice_draft' else 'partner_change';model='account.move' if kind=='invoice_draft' else 'res.partner'
            prior=c.execute('SELECT body FROM external_links WHERE connection_id=? AND model=? AND external_id=? AND local_kind=?',(connection['id'],model,str(result['remote_id']),kind)).fetchone()
            if prior:
                link=json.loads(prior['body']);self.db.put(c,cid,'integration_link_history',link)
                link.update(local_id=local_id,source_hash=final['source_hash'],last_seen_at=now())
                c.execute('UPDATE external_links SET local_id=?,source_hash=?,body=? WHERE id=?',(local_id,final['source_hash'],canonical(link),link['id']))
            else:self._link(c,connection,model,result['remote_id'],kind,local_id,final['source_hash'],result.get('write_date'))
            c.execute('UPDATE idempotency_keys SET state=?,body=? WHERE company_id=? AND connection_id=? AND operation=? AND key=?',('succeeded',canonical(final),cid,connection['id'],'write',key))
            # The proposal is append-only. Execution state lives in idempotency_keys to retain its signed hash.
            event(self.db,c,connection,actor,'invoice_draft.created' if result['kind']=='invoice_draft' else 'sync.completed',{'operation':'write_completed','proposalId':proposal['id'],'remoteId':result['remote_id']},correlation)
        return final

    def reconcile_write(self,actor,cid,key,correlation):
        connection,server=self.scope(actor,cid,'writes.commit')
        with self.db.connection() as c:
            row=c.execute('SELECT body,state FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation=? AND key=?',(cid,connection['id'],'write',key)).fetchone()
            if not row:reject('not_found','Operación no encontrada',404)
            intent=json.loads(row['body'])
            if row['state']=='succeeded':return intent
            proposal=self._get_proposal(c,cid,connection['id'],intent['proposal_id'])
        result=self.client(actor,cid,'writes.commit',connection).call('agntia.bridge','operation_status',{'company_id':server.odoo_company_id,'operation_key':intent['operation_key']})
        if not result:return {**intent,'status':'reconciliation_required','notice':'No se observa confirmación remota. No se reintenta la escritura automáticamente.'}
        return self._finish_write(actor,cid,connection,key,intent,proposal,result,correlation)
