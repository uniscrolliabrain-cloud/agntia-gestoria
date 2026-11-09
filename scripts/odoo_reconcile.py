"""Read/reconcile an existing synthetic write; never retries create."""
import argparse,json,os
from odoo_bootstrap import state_dir
p=argparse.ArgumentParser();p.add_argument('--state-dir',required=True);p.add_argument('--company-id',required=True);p.add_argument('--idempotency-key',required=True);args=p.parse_args();state=state_dir(args.state_dir)
for key,value in json.loads((state/'run-env.json').read_text()).items():os.environ[key]=value
from agntia_gestoria.storage import Database
from agntia_gestoria.integrations.odoo.adapter import Adapter
from agntia_gestoria.auth import Actor
adapter=Adapter(Database(state/'gestoria-data'))
result=adapter.reconcile_write(Actor('owner','owner',('*',)),args.company_id,args.idempotency_key,'synthetic-manual-reconcile')
print(json.dumps({'status':result['status'],'reconciliation_required':result.get('reconciliation_required'),'remote_id':result.get('remote_id')}))
