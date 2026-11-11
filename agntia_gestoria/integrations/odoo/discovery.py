from datetime import datetime,timezone,timedelta
from ...storage import digest,now
from ..errors import reject,IntegrationError

FIELDS={
 'res.partner':{'id','name','vat','email','company_id','write_date'},
 'account.move':{'id','state','move_type','company_id','invoice_line_ids','currency_id','write_date'},
 'account.move.line':{'id','move_id','company_id','display_type','price_subtotal','price_total','tax_ids'},
 'account.tax':{'id','company_id','amount_type','amount','type_tax_use','price_include'},
 'account.journal':{'id','company_id','type'},
 'account.account':{'id','company_ids','account_type'},
 'ir.attachment':{'id','res_model','res_id','file_size','mimetype'},
}


def discover(client,server):
    info=client.call('agntia.bridge','server_info',{'company_id':server.odoo_company_id})
    if not isinstance(info,dict) or info.get('version')!='19.0' or info.get('bridge_version')!='1.0':reject('unsupported','Se requiere Odoo Community 19 y agntia_bridge 1.0',424)
    if info.get('source_revision')!=server.expected_source_revision or info.get('enterprise_installed'):
        reject('unsupported','No se ha verificado el código Community fijado',424)
    if info.get('instance_id')!=server.expected_instance_id or info.get('company_id')!=server.odoo_company_id:reject('scope_violation','Identidad de instancia o compañía diferente',424)
    if info.get('superuser') or info.get('settings_admin') or type(info.get('uid'))!=int or info['uid']<=1:reject('unsafe_principal','La cuenta Odoo no cumple privilegios mínimos',424)
    companies=info.get('allowed_company_ids',[])
    if server.odoo_company_id not in companies or (not server.allow_multi_company and companies!=[server.odoo_company_id]):reject('scope_violation','Cuenta Odoo multicompañía no autorizada',424)
    supported={};unsupported=[];verified={}
    for model,required in FIELDS.items():
        try:
            metadata=client.call(model,'fields_get',{'attributes':['type','readonly']})
            ok=isinstance(metadata,dict) and required<=metadata.keys() and info.get('read_access',{}).get(model) is True
            verified[model]=sorted(required & metadata.keys()) if isinstance(metadata,dict) else []
        except IntegrationError as exc:
            if exc.code not in ('unsupported','provider_auth','provider_validation'):raise
            ok=False;verified[model]=[]
        if not ok:unsupported.append(model)
        supported[model]=ok
    capabilities=[]
    if supported.get('res.partner'):capabilities.append('contacts.read')
    if all(supported.get(x) for x in ('account.move','account.move.line','account.tax')):capabilities.append('invoices.read')
    if supported.get('ir.attachment') and 'invoices.read' in capabilities:capabilities.append('attachments.read')
    if server.write_enabled and info.get('write_access',{}).get('res.partner'):capabilities.append('partners.write')
    if server.write_enabled and 'invoices.read' in capabilities and info.get('write_access',{}).get('account.move'):capabilities.append('invoice_drafts.write')
    evidence={'source_revision':info['source_revision'],'version':info['version'],'bridge_version':info['bridge_version'],'uid':info['uid'],'instance_id':info['instance_id'],'company_id':info['company_id'],'modules':info.get('modules',{}),'fields':verified}
    return {'checked_at':now(),'expires_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'capabilities':capabilities,'unsupported':unsupported,'evidence_hash':digest(evidence),'evidence':evidence,'identity_vat':info.get('company_vat') or ''}
