"""Reproduce local C01 diagnostics, not a replacement for the unmodified CI suite.
No network credentials, real databases or Odoo calls are used.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'local-results'
OUT.mkdir(exist_ok=True)
python=str(ROOT/'.venv/bin/python')
checks=[
 ('install-dev-offline',[python,'-m','pip','install','--no-index','--no-build-isolation','-e','.[dev]'],20),
 ('install-runtime-offline',[python,'-m','pip','install','--no-index','--no-build-isolation','-e','.'],20),
 ('unit-standard',[python,'-m','unittest','discover','-s','tests','-v'],15),
 ('unit-selector-workaround',[python,'-c',"import selectors,unittest; original=selectors.DefaultSelector.select; selectors.DefaultSelector.select=lambda self,timeout=None:original(self,min(.02,timeout) if timeout is not None else .02); r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"],30),
 ('node-build',['node','typescript/scripts/build.mjs'],15),
 ('node-app-syntax',['node','--check','agntia_gestoria/static/app.js'],10),
 ('node-dashboard-syntax',['node','--check','agntia_gestoria/static/dashboard.js'],10),
 ('node-dist-unchanged',['git','diff','--exit-code','--','typescript/dist'],10),
 ('python-compile',[python,'-m','compileall','-q','agntia_gestoria','tests','scripts'],10),
 ('baseline-inventory',[python,'scripts/verify_baseline.py'],10),
 ('browser-local',[python,'scripts/browser_check.py'],15),
 ('docker-local-socket',['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock','info','--format','{{.ServerVersion}}'],10),
]
results=[]
for name,command,timeout in checks:
    start=time.monotonic()
    try:
        completed=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        output=completed.stdout.decode(errors='replace');code=completed.returncode;timed_out=False
    except subprocess.TimeoutExpired as error:
        output=(error.stdout or b'').decode(errors='replace');code=124;timed_out=True
    elapsed=round(time.monotonic()-start,3)
    # Fixed commands and synthetic fixtures only; do not generalize this runner to real secrets/data.
    output=output.replace(str(ROOT),'<CHECKOUT>').replace('/home/agent','<USER_HOME>')
    (OUT/(name+'.log')).write_text(output)
    result={'name':name,'exit_code':code,'timed_out':timed_out,'elapsed_seconds':elapsed,'command':command,'log':name+'.log'}
    result['command']=[v.replace(str(ROOT),'<CHECKOUT>') for v in result['command']]
    results.append(result);print(json.dumps({k:result[k] for k in ('name','exit_code','timed_out','elapsed_seconds')}),flush=True)
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
