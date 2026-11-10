from datetime import datetime,timedelta
from ..errors import reject
from .mappers.partner import partner,remote_id
from .mappers.invoice import invoice


def pages(client,model,company,fields,watermark=None,maximum=100000):
    last_id=0;seen=0
    while True:
        domain=[['company_id','=',company],['id','>',last_id]]
        if watermark:domain.append(['write_date','>=',watermark])
        rows=client.call(model,'search_read',{'domain':domain,'fields':fields,'order':'id asc','limit':100})
        if not isinstance(rows,list) or len(rows)>100:reject('invalid_response','Página Odoo inválida',502)
        if not rows:return
        for row in rows:
            if not isinstance(row,dict) or type(row.get('id'))!=int or row['id']<=last_id or remote_id(row.get('company_id'))!=company:reject('scope_violation','Página remota fuera de ámbito o desordenada',502)
            last_id=row['id'];seen+=1
            if seen>maximum:reject('limit','Barrido supera el presupuesto configurado',422)
        yield rows
        if len(rows)<100:return


def read_partners(client,server,watermark=None):
    fields=['id','name','vat','email','is_company','country_id','company_id','write_date']
    for rows in pages(client,'res.partner',server.odoo_company_id,fields,watermark):
        yield [{'model':'res.partner','external_id':str(r['id']),'write_date':r.get('write_date'),'source':r,'normalized':partner(r,server.odoo_company_id),'blocked':False,'warnings':[]} for r in rows]


def read_invoices(client,server,connection_id,watermark=None):
    fields=['id','company_id','move_type','state','write_date']
    for rows in pages(client,'account.move',server.odoo_company_id,fields,watermark):
        selected=[r for r in rows if r.get('move_type') in ('out_invoice','in_invoice','out_refund','in_refund')]
        if not selected:continue
        snapshots=client.call('agntia.bridge','invoice_snapshots',{'company_id':server.odoo_company_id,'invoice_ids':[r['id'] for r in selected]})
        if not isinstance(snapshots,list) or len(snapshots)!=len(selected) or any(not isinstance(s,dict) or not isinstance(s.get('move'),dict) for s in snapshots) or {s['move'].get('id') for s in snapshots}!={r['id'] for r in selected}:reject('invalid_response','Snapshot de facturas incompleto',502)
        output=[]
        for snapshot in snapshots:
            mapped=invoice(snapshot,server,connection_id)
            output.append({'model':'account.move','external_id':str(mapped['move_id']),'write_date':mapped['write_date'],'source':snapshot,'normalized':mapped,'blocked':mapped['blocked'],'warnings':mapped['warnings']})
        yield output
