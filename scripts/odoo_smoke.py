"""Explicit real-provider smoke against the separately provisioned synthetic lab."""
import argparse,json,os,sys,uuid
from pathlib import Path
from odoo_bootstrap import state_dir
p=argparse.ArgumentParser();p.add_argument('--state-dir',required=True);p.add_argument('--output');args=p.parse_args();state=state_dir(args.state_dir)
settings=json.loads((state/'run-env.json').read_text())
for k,v in settings.items():os.environ[k]=v
from agntia_gestoria.app import create_app
from agntia_gestoria.auth import Actor
from agntia_gestoria.integrations.odoo.adapter import Adapter
from agntia_gestoria.integrations.contracts import ConnectionCreate,BindingValidation
fixtures=json.loads((state/'fixtures.private.json').read_text())
app=create_app(str(state/'gestoria-data'));adapter=Adapter(app.state.db);owner=Actor('owner','owner',('*',));out=[]
for fixture in fixtures['companies']:
 cid=fixture['gestoria_company_id']
 try:connection,_=adapter.scope(owner,cid,'connections.manage',ready=False)
 except Exception:
  adapter.create_connection(owner,cid,ConnectionCreate(server_ref=fixture['server_ref']),'synthetic-smoke');connection,_=adapter.scope(owner,cid,'connections.manage',ready=False)
 adapter.validate(owner,cid,BindingValidation(revision=connection['revision'],confirm_fiscal_identity=True,notes='Synthetic fixture identity explicitly verified'),'synthetic-smoke')
 result=adapter.preview(owner,cid,'invoices',True,'synthetic-smoke');imported=adapter.import_stages(owner,cid,result['staging_ids'],'synthetic-smoke-'+uuid.uuid4().hex,'synthetic-smoke')
 out.append({'company_id':cid,'health':adapter.capabilities(owner,cid),'staged':result['count'],'import_result':imported,'audit':adapter.audit_integrity(owner,cid)})
# Sentinel secrets may not enter public smoke output.
text=json.dumps({'runtime_test':'executed','results':out},indent=2)
for secret in [settings['GESTORIA_OWNER_TOKEN'],settings['ODOO_BRIDGE_SIGNING_KEY'],*[f['api_key'] for f in fixtures['companies']]]:
 if secret in text:raise SystemExit('Secret sentinel reached smoke output')
if args.output:Path(args.output).write_text(text+'\n')
print(json.dumps({'runtime_smoke':'PASS','companies_checked':len(out)}))
