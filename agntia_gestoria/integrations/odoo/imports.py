import json
from datetime import datetime,timedelta,timezone
from ...storage import canonical,digest,now,uid,identifier
from ..errors import reject
from .evidence import event
from .reads import read_partners,read_invoices


class Imports:
    def preview(self,actor,cid,resource,full,correlation,heartbeat=None):
        connection,server=self.scope(actor,cid,'imports.run');self.require_capability(connection,'contacts.read' if resource=='partners' else 'invoices.read')
        client=self.client(actor,cid,'imports.run',connection)
        watermark=None
        with self.db.connection() as c:
            row=c.execute('SELECT body FROM sync_cursors WHERE connection_id=? AND resource=?',(connection['id'],resource)).fetchone()
            if row and not full:
                cursor=json.loads(row['body'])
                if cursor.get('write_date'):watermark=(datetime.fromisoformat(cursor['write_date'])-timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
        pages=read_partners(client,server,watermark) if resource=='partners' else read_invoices(client,server,connection['id'],watermark)
        ids=[];seen=[];maximum=watermark;maximum_id=0
        for page in pages:
            if heartbeat:heartbeat()
            with self.db.transaction() as c:
                self._connection(c,cid,connection['id'])
                for item in page:
                    source_hash=digest(item['source']);seen.append(item['external_id'])
                    if item.get('write_date'):
                        stamp=str(item['write_date'])
                        if maximum is None or (stamp,int(item['external_id']))>(maximum,maximum_id):maximum=stamp;maximum_id=int(item['external_id'])
                    old=c.execute('SELECT id FROM integration_staging WHERE connection_id=? AND model=? AND external_id=? AND source_hash=?',(connection['id'],item['model'],item['external_id'],source_hash)).fetchone()
                    if old:ids.append(old['id']);continue
                    stage={**item,'id':uid(),'company_id':cid,'connection_id':connection['id'],'source_hash':source_hash,'state':'mapping_blocked' if item['blocked'] else 'staged','mapping_version':'odoo19-v1','created_at':now()}
                    c.execute('INSERT INTO integration_staging VALUES(?,?,?,?,?,?,?,?)',(stage['id'],cid,connection['id'],item['model'],item['external_id'],source_hash,stage['state'],canonical(stage)));ids.append(stage['id'])
                    link=c.execute('SELECT body FROM external_links WHERE connection_id=? AND model=? AND external_id=? AND local_kind=?',(connection['id'],item['model'],item['external_id'],'partner' if resource=='partners' else 'invoice')).fetchone()
                    if link and source_hash not in (json.loads(link['body'])['source_hash'],json.loads(link['body']).get('acknowledged_remote_hash')):
                        stage['state']='conflict';c.execute('UPDATE integration_staging SET state=?,body=? WHERE id=?',('conflict',canonical(stage),stage['id']))
                        self._conflict(c,connection,actor,json.loads(link['body']),'remote_cancelled' if item['normalized'].get('state')=='cancel' else 'remote_changed',stage['id'],correlation)
        with self.db.transaction() as c:
            if full:
                model='res.partner' if resource=='partners' else 'account.move';kind='partner' if resource=='partners' else 'invoice'
                for row in c.execute('SELECT body FROM external_links WHERE connection_id=? AND model=? AND local_kind=?',(connection['id'],model,kind)).fetchall():
                    link=json.loads(row['body'])
                    if link['external_id'] not in seen and not link.get('acknowledged_missing'):self._conflict(c,connection,actor,link,'remote_missing',None,correlation)
            prior_cursor=c.execute('SELECT body FROM sync_cursors WHERE connection_id=? AND resource=?',(connection['id'],resource)).fetchone()
            if prior_cursor:
                prior=json.loads(prior_cursor['body'])
                if prior.get('write_date') and (maximum is None or prior['write_date']>maximum):maximum=prior['write_date'];maximum_id=prior.get('external_id',0)
            cursor={'write_date':maximum,'external_id':maximum_id,'last_sync_at':now(),'full':full}
            c.execute('INSERT INTO sync_cursors VALUES(?,?,?) ON CONFLICT(connection_id,resource) DO UPDATE SET body=excluded.body',(connection['id'],resource,canonical(cursor)))
            event(self.db,c,connection,actor,'sync.completed',{'resource':resource,'staged':len(ids),'full':full},correlation)
        return {'staging_ids':ids,'count':len(ids),'cursor':cursor}

    def _conflict(self,c,connection,actor,link,reason,stage_id,correlation):
        existing=c.execute("SELECT body FROM integration_conflicts WHERE connection_id=? AND state='open' AND json_extract(body,'$.model')=? AND json_extract(body,'$.external_id')=?",(connection['id'],link['model'],link['external_id'])).fetchone()
        if existing:return json.loads(existing['body'])
        conflict={'id':uid(),'company_id':connection['company_id'],'connection_id':connection['id'],'model':link['model'],'external_id':link['external_id'],'link_id':link['id'],'stage_id':stage_id,'reason':reason,'state':'open','revision':0,'created_at':now(),'marker_ids':[]}
        if link['local_kind']=='invoice':
            rows=c.execute('SELECT body FROM external_links WHERE connection_id=? AND local_kind=?',(connection['id'],'tax_record')).fetchall()
            for row in rows:
                line_link=json.loads(row['body'])
                if line_link.get('remote_invoice_id')!=int(link['external_id']):continue
                record=self.db.get(c,connection['company_id'],line_link['local_id'],'tax_record')
                marker={'id':uid(),'company_id':connection['company_id'],'external_id':'odoo-conflict:'+conflict['id']+':'+record['id'],'operation_date':record['operation_date'],'kind':'adjustment','description':'Cambio remoto pendiente de revisión; no liquidar hasta resolver','tax_kind':'other','base_amount':'0.00','tax_amount':'0.00','withholding_amount':'0.00','document_ids':[],'category':'other','vat_treatment':'other','tax_rate':None,'deductible_tax_amount':None,'deductible_irpf_amount':None,'classification_notes':'Bloqueo por conflicto de procedencia Odoo','revision':0,'status':'unverified','created_at':now(),'created_by':actor.id,'provenance_conflict':conflict['id']}
                self.db.put(c,connection['company_id'],'tax_record',marker,'tax-record:'+marker['external_id']);self.db.audit(c,connection['company_id'],actor,'integration.source_invalidated',marker['id'],marker);conflict['marker_ids'].append(marker['id'])
        c.execute('INSERT INTO integration_conflicts VALUES(?,?,?,?,?,?)',(conflict['id'],connection['company_id'],connection['id'],'open',0,canonical(conflict)))
        case={'id':uid(),'company_id':connection['company_id'],'revision':0,'status':'draft','created_at':now(),'created_by':actor.id,'review':None,'title':'Revisar cambio o ausencia en Odoo','category':'accounting','description':'Conflicto '+conflict['id']+'. No se modifica el registro revisado ni se elimina el objeto remoto.','due_date':None,'source_ids':[],'document_ids':[]}
        self.db.put(c,connection['company_id'],'case',case);self.db.audit(c,connection['company_id'],actor,'integration.conflict_case.created',case['id'],case)
        event(self.db,c,connection,actor,'conflict.detected',{'conflictId':conflict['id'],'reason':reason,'evidenceIds':[]},correlation)
        return conflict

    def _link(self,c,connection,model,external,kind,local,source_hash,write_date,**metadata):
        link={'id':uid(),'gestoria_company_id':connection['company_id'],'company_id':connection['company_id'],'connection_id':connection['id'],'provider':'odoo_community','model':model,'external_id':str(external),'local_kind':kind,'local_id':local,'remote_write_date':write_date,'source_hash':source_hash,'mapping_version':'odoo19-v1','last_seen_at':now(),'sync_status':'linked',**metadata}
        c.execute('INSERT INTO external_links VALUES(?,?,?,?,?,?,?,?,?)',(link['id'],connection['company_id'],connection['id'],model,str(external),kind,local,source_hash,canonical(link)))
        return link

    def import_stages(self,actor,cid,stage_ids,key,correlation):
        connection,server=self.scope(actor,cid,'imports.run');payload_hash=digest(sorted(stage_ids))
        with self.db.connection() as c:
            previous=c.execute('SELECT payload_hash,body FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation=? AND key=?',(cid,connection['id'],'import_apply',key)).fetchone()
            if previous:
                if previous['payload_hash']!=payload_hash:reject('idempotency_conflict','Clave reutilizada con otro lote',409)
                return json.loads(previous['body'])
            to_check=[]
            for sid in stage_ids:
                row=c.execute('SELECT body FROM integration_staging WHERE id=? AND company_id=? AND connection_id=?',(identifier(sid),cid,connection['id'])).fetchone()
                if not row:reject('not_found','Recurso no encontrado',404)
                stage=json.loads(row['body'])
                if stage['state'] not in ('mapping_blocked','imported','conflict'):to_check.append(stage)
        client=self.client(actor,cid,'imports.run',connection)
        for stage in to_check:
            if stage['model']=='account.move':
                remote=client.call('agntia.bridge','invoice_snapshots',{'company_id':server.odoo_company_id,'ids':[int(stage['external_id'])]})
                current=remote[0] if isinstance(remote,list) and len(remote)==1 else None
            else:
                remote=client.call('res.partner','search_read',{'domain':[['id','=',int(stage['external_id'])],['company_id','=',server.odoo_company_id]],'fields':['id','name','vat','email','is_company','country_id','company_id','write_date'],'limit':1})
                current=remote[0] if isinstance(remote,list) and len(remote)==1 else None
            if current is None or digest(current)!=stage['source_hash']:reject('source_changed','La fuente cambió desde la vista previa; generar un staging nuevo',409)
        with self.db.transaction() as c:
            previous=c.execute('SELECT payload_hash,body FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation=? AND key=?',(cid,connection['id'],'import_apply',key)).fetchone()
            if previous:
                if previous['payload_hash']!=payload_hash:reject('idempotency_conflict','La clave ya identifica otro lote',409)
                return json.loads(previous['body'])
            result={'imported':0,'unchanged':0,'conflicts':0,'mapping_blocked':0,'local_ids':[]}
            stages=[]
            for sid in stage_ids:
                row=c.execute('SELECT body FROM integration_staging WHERE id=? AND company_id=? AND connection_id=?',(identifier(sid),cid,connection['id'])).fetchone()
                if not row:reject('not_found','Recurso no encontrado',404)
                stages.append(json.loads(row['body']))
            for stage in stages:
                if stage['state']=='mapping_blocked':result['mapping_blocked']+=1;continue
                kind='partner' if stage['model']=='res.partner' else 'invoice'
                prior=c.execute('SELECT body FROM external_links WHERE connection_id=? AND model=? AND external_id=? AND local_kind=?',(connection['id'],stage['model'],stage['external_id'],kind)).fetchone()
                if prior:
                    link=json.loads(prior['body'])
                    if stage['source_hash'] in (link['source_hash'],link.get('acknowledged_remote_hash')):result['unchanged']+=1;continue
                    self._conflict(c,connection,actor,link,'remote_changed',stage['id'],correlation);result['conflicts']+=1;continue
                if stage['model']=='res.partner':
                    obj={'id':uid(),'company_id':cid,'status':'original_unverified',**stage['normalized'],'source_hash':stage['source_hash'],'created_at':now()}
                    self.db.put(c,cid,'erp_partner',obj);self._link(c,connection,'res.partner',stage['external_id'],'partner',obj['id'],stage['source_hash'],stage['write_date']);result['local_ids'].append(obj['id'])
                else:
                    obj={'id':uid(),'company_id':cid,'status':'original_unverified','remote_state':stage['normalized']['state'],'source_hash':stage['source_hash'],'source_snapshot':stage['source'],'created_at':now()}
                    self.db.put(c,cid,'erp_invoice',obj);self._link(c,connection,'account.move',stage['external_id'],'invoice',obj['id'],stage['source_hash'],stage['write_date'])
                    for fact in stage['normalized']['facts']:
                        record={**fact['record'],'id':uid(),'company_id':cid,'revision':0,'status':'unverified','created_at':now(),'created_by':actor.id,'provenance':{'connection_id':connection['id'],'remote_invoice_id':int(stage['external_id']),'remote_line_id':fact['remote_line_id'],'source_hash':stage['source_hash'],'source_state':stage['normalized']['state'],'mapping_version':'odoo19-v1'}}
                        self.db.put(c,cid,'tax_record',record,'tax-record:'+record['external_id']);self._link(c,connection,'account.move.line',fact['remote_line_id'],'tax_record',record['id'],stage['source_hash'],stage['write_date'],remote_invoice_id=int(stage['external_id']));self.db.audit(c,cid,actor,'integration.tax_record.imported',record['id'],record);result['local_ids'].append(record['id'])
                result['imported']+=1;stage['state']='imported';c.execute('UPDATE integration_staging SET state=?,body=? WHERE id=?',('imported',canonical(stage),stage['id']))
                self.db.audit(c,cid,actor,'integration.source.imported',obj['id'],obj)
            c.execute('INSERT INTO idempotency_keys VALUES(?,?,?,?,?,?,?)',(cid,connection['id'],'import_apply',key,payload_hash,'succeeded',canonical(result)))
            event(self.db,c,connection,actor,'review.required',{'imported':result['imported'],'conflicts':result['conflicts'],'evidenceIds':result['local_ids']},correlation)
        return result

    def resolve_conflict(self,actor,cid,conflict_id,revision,decision,notes,correlation):
        connection,_=self.scope(actor,cid,'conflicts.resolve',ready=False)
        if decision not in ('keep_local','supersede_local') or len(notes)<5:reject('validation','Decisión o motivo inválido',422)
        with self.db.transaction() as c:
            row=c.execute('SELECT body FROM integration_conflicts WHERE id=? AND company_id=? AND connection_id=?',(identifier(conflict_id),cid,connection['id'])).fetchone()
            if not row:reject('not_found','Recurso no encontrado',404)
            item=json.loads(row['body'])
            if item['state']!='open' or item['revision']!=revision:reject('conflict','Conflicto ya modificado',409)
            if decision=='supersede_local':
                if not item.get('stage_id'):reject('validation','No hay sustitución remota disponible',422)
                row=c.execute('SELECT body FROM integration_staging WHERE id=? AND company_id=?',(item['stage_id'],cid)).fetchone();stage=json.loads(row['body'])
                if stage['blocked']:reject('mapping_blocked','No se puede aceptar un mapeo bloqueado',422)
                links=c.execute('SELECT body FROM external_links WHERE connection_id=?',(connection['id'],)).fetchall()
                for row in links:
                    link=json.loads(row['body'])
                    if link['id']==item['link_id'] or link.get('remote_invoice_id')==int(item['external_id']):
                        if link['local_kind']=='tax_record':
                            record=self.db.get(c,cid,link['local_id'],'tax_record');record.update(status='void',revision=record['revision']+1,voided_at=now(),superseded_by_conflict=item['id']);self.db.put(c,cid,'tax_record',record);self.db.audit(c,cid,actor,'integration.tax_record.superseded',record['id'],record)
                        link['sync_status']='detached';self.db.put(c,cid,'integration_link_history',link);c.execute('DELETE FROM external_links WHERE id=?',(link['id'],))
                stage['state']='staged';c.execute('UPDATE integration_staging SET state=?,body=? WHERE id=?',('staged',canonical(stage),stage['id']))
            else:
                # Keep local values explicitly; acknowledge the observed version without replacing financial data.
                if item.get('stage_id'):
                    stage=json.loads(c.execute('SELECT body FROM integration_staging WHERE id=?',(item['stage_id'],)).fetchone()['body'])
                    link=json.loads(c.execute('SELECT body FROM external_links WHERE id=?',(item['link_id'],)).fetchone()['body']);link['acknowledged_remote_hash']=stage['source_hash']
                    c.execute('UPDATE external_links SET body=? WHERE id=?',(canonical(link),link['id']))
                elif item['reason']=='remote_missing':
                    link=json.loads(c.execute('SELECT body FROM external_links WHERE id=?',(item['link_id'],)).fetchone()['body']);link['acknowledged_missing']=True
                    c.execute('UPDATE external_links SET body=? WHERE id=?',(canonical(link),link['id']))
            for marker_id in item['marker_ids']:
                marker=self.db.get(c,cid,marker_id,'tax_record');marker.update(status='void',revision=marker['revision']+1,voided_at=now());self.db.put(c,cid,'tax_record',marker);self.db.audit(c,cid,actor,'integration.conflict_marker.resolved',marker_id,marker)
            item.update(state='resolved',revision=revision+1,resolution={'decision':decision,'notes':notes,'actor_id':actor.id,'at':now()})
            c.execute('UPDATE integration_conflicts SET state=?,revision=?,body=? WHERE id=?',('resolved',item['revision'],canonical(item),item['id']))
            event(self.db,c,connection,actor,'sync.completed',{'operation':'conflict_resolved','conflictId':item['id']},correlation)
        return item
