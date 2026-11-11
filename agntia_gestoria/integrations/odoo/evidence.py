import json
import re
from ...storage import canonical,digest,now,uid


def event(db,c,connection,actor,kind,payload,correlation_id,causation_id=None):
    obj={'id':uid(),'schemaVersion':1,'type':'gestoria.odoo.'+kind,'source':'agntia-gestoria','tenantId':connection['tenant_id'],'companyId':connection['company_id'],'correlationId':correlation_id,'causationId':causation_id,'occurredAt':now(),'payload':{'connectionId':connection['id'],**payload}}
    c.execute('INSERT INTO integration_outbox VALUES(?,?,?,?,?)',(obj['id'],connection['company_id'],connection['id'],'pending',canonical(obj)))
    db.audit(c,connection['company_id'],actor,'integration.'+kind,obj['id'],obj)
    return obj


def verify_audit(db,c,cid):
    previous='0'*64;count=0;last=0
    for item in db.audit_log(c,cid):
        hashed=item.pop('hash');seq=item.pop('sequence')
        if seq<=last or item.get('previous_hash')!=previous or digest(item)!=hashed or not re.fullmatch(r'[a-f0-9]{64}',item.get('content_hash','')):return {'valid':False,'checked':count,'failure_sequence':seq,'limitation':'No demuestra inmutabilidad frente a un administrador que reescribe la cadena completa.'}
        evidence=c.execute('SELECT body FROM integration_outbox WHERE id=? AND company_id=?',(item.get('object_id'),cid)).fetchone()
        if evidence and item.get('action')!='integration.event.acked' and digest(json.loads(evidence['body']))!=item['content_hash']:
            return {'valid':False,'checked':count,'failure_sequence':seq,'reason':'immutable_event_content_mismatch'}
        previous=hashed;last=seq;count+=1
    return {'valid':True,'checked':count,'head_hash':previous,'limitation':'Valida enlaces e integridad interna; no sustituye firma o archivo inmutable externo.'}
