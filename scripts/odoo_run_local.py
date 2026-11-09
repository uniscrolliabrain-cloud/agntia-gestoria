"""Run the synthetic lab's API/worker on the host without printing credentials."""
import argparse,json,os
from pathlib import Path
from odoo_bootstrap import state_dir

p=argparse.ArgumentParser();p.add_argument('--state-dir',required=True);p.add_argument('--worker',action='store_true');p.add_argument('--once',action='store_true');p.add_argument('--port',type=int,default=8010);args=p.parse_args()
state=state_dir(args.state_dir)
for key,value in json.loads((state/'run-env.json').read_text()).items():
    if not key.startswith(('GESTORIA_','ODOO_')) or not isinstance(value,str):raise SystemExit('Unexpected lab environment variable')
    os.environ[key]=value
if args.worker:
    from agntia_gestoria.integrations.migrations import migrate
    from agntia_gestoria.integrations.odoo.adapter import Adapter
    from agntia_gestoria.storage import Database
    import time
    db=Database(state/'gestoria-data');migrate(db);adapter=Adapter(db)
    while True:
        result=adapter.run_one()
        if result:print(json.dumps({'job_id':result['job_id'],'state':result['state']}),flush=True)
        if args.once:break
        if not result:time.sleep(1)
else:
    import uvicorn
    uvicorn.run('agntia_gestoria.app:create_app',factory=True,host='127.0.0.1',port=args.port)
