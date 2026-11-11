import json
import os
from ..auth import company_access,require_role,actors,Actor
from .errors import IntegrationError,reject

READ={'health','contacts.read','invoices.read','jobs.read','conflicts.read','events.read','metrics.read'}
PROPOSE={'events.ack','imports.run','partners.propose','invoices.propose'}
HUMAN={'connections.manage','approvals.create','writes.commit','conflicts.resolve','records.classify','attachments.download'}
ALL=READ|PROPOSE|HUMAN


def enabled():return os.getenv('ODOO_ADAPTER_ENABLED','false').lower()=='true'


def authorize(actor,cid,tenant,capability):
    if not enabled():reject('disabled','El adaptador Odoo está desactivado',424)
    company_access(actor,cid)
    configured=actors()
    if configured:
        matches=[a for _,a in configured if a.id==actor.id]
        if len(matches)!=1 or matches[0]!=actor:reject('principal_revoked','Principal revocado o ambiguo',403)
    elif actor!=Actor('local-owner','owner',('*',)) or os.getenv('ODOO_ALLOW_LOCAL_OWNER')!='true':
        reject('principal_revoked','Se requiere un principal configurado para Odoo',403)
    if capability not in ALL:reject('forbidden','Capacidad desconocida',403)
    if capability in HUMAN:require_role(actor,'owner','reviewer')
    elif capability in PROPOSE:require_role(actor,'owner','reviewer','agent')
    scopes=json.loads(os.getenv('ODOO_ACTOR_SCOPES_JSON','{}'))
    mode=os.getenv('ODOO_IDENTITY_MODE','standalone')
    if mode=='standalone':
        if tenant!='standalone:'+cid:reject('not_found','Recurso no encontrado',404)
    elif mode=='integrated':
        scope=scopes.get(actor.id,{})
        if scope.get('tenant_id')!=tenant or cid not in scope.get('companies',[]) or capability not in scope.get('capabilities',[]):reject('not_found','Recurso no encontrado',404)
    else:reject('configuration','Modo de identidad inválido',503)


def tenant_for(actor,cid):
    company_access(actor,cid)
    if os.getenv('ODOO_IDENTITY_MODE','standalone')=='standalone':return 'standalone:'+cid
    scope=json.loads(os.getenv('ODOO_ACTOR_SCOPES_JSON','{}')).get(actor.id,{})
    if cid not in scope.get('companies',[]) or not scope.get('tenant_id'):reject('not_found','Recurso no encontrado',404)
    return scope['tenant_id']


def actor_for_job(actor_id):
    matches=[a for _,a in actors() if a.id==actor_id]
    if len(matches)==1:return matches[0]
    if not matches and actor_id=='local-owner' and os.getenv('ODOO_ALLOW_LOCAL_OWNER')=='true':return Actor('local-owner','owner',('*',))
    reject('principal_revoked','Principal revocado o ambiguo',403)
