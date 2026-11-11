"""Prepare/build an isolated synthetic lab. No implicit reset, deletion or production access."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
MARKER='AGNTIA_SYNTHETIC_LAB.json'


def state_dir(value,create=False):
    path=Path(value).resolve()
    if path in (Path(path.anchor),ROOT,Path.home()):raise SystemExit('Unsafe state directory')
    if ROOT==path or ROOT in path.parents:raise SystemExit('Lab secrets must be outside the repository')
    if create:
        if path.exists() and any(path.iterdir()):raise SystemExit('Refusing to overwrite an existing state directory')
        path.mkdir(parents=True,exist_ok=True);path.chmod(0o700)
        (path/MARKER).write_text(json.dumps({'synthetic':True,'project':'agntia-gestoria-synthetic-lab','id':uuid.uuid4().hex}))
    elif not (path/MARKER).is_file():raise SystemExit('Synthetic marker required')
    return path


def compose(state,*args,input=None,capture=False):
    # Refuse potentially inherited remote Docker selectors. The owner selects a local context separately.
    if os.getenv('DOCKER_HOST'):raise SystemExit('DOCKER_HOST is set; verify a local test daemon explicitly before proceeding')
    env={**os.environ,'AGNTIA_LAB_STATE_DIR':str(state)}
    result=subprocess.run(['docker','compose','--project-name','agntia-gestoria-synthetic-lab','-f',str(ROOT/'infra/odoo/compose.yaml'),*args],input=input,text=True,env=env,capture_output=capture)
    if result.returncode:
        if capture:
            log=state/'private-bootstrap-failure.log';log.write_text((result.stdout or '')+'\n'+(result.stderr or ''))
        raise SystemExit('Synthetic lab command failed; inspect private logs without publishing secrets')
    return result.stdout if capture else None


def prepare(state):
    folder=state/'secrets';folder.mkdir()
    (folder/'postgres_password').write_text(secrets.token_urlsafe(36))
    (folder/'bridge_signing_key').write_text(secrets.token_urlsafe(48))
    config=(ROOT/'infra/odoo/odoo.conf').read_text()
    # docker exec does not run the image entrypoint which supplies DB_ARGS.
    # Keep shell/init connections configured in the same private mounted file.
    config+='\ndb_host = db\ndb_port = 5432\ndb_user = odoo\ndb_password = '+(folder/'postgres_password').read_text().strip()+'\nadmin_passwd = '+secrets.token_urlsafe(48)+'\n'
    (state/'odoo.conf').write_text(config)
    (state/'gestoria.env.local').write_text('# Generated after fixture bootstrap\n')
    print('Private synthetic state prepared; protect this directory with owner-only NTFS/OS access')


def bootstrap(state):
    compose(state,'up','-d','--build','db','odoo')
    fixtures=[]
    for database in ('agntia_test_a','agntia_test_b'):
        compose(state,'exec','-T','odoo','odoo','-d',database,'-i','base,contacts,account,l10n_es,agntia_bridge,agntia_bridge_account','--without-demo=true','--stop-after-init','--no-http')
        script=(ROOT/'scripts/odoo_fixture.py').read_text()
        output=compose(state,'exec','-T','odoo','odoo','shell','-d',database,'--no-http','--shell-interface','python',input=script,capture=True)
        lines=[line.split('AGNTIA_FIXTURE_RESULT:',1)[1] for line in output.splitlines() if 'AGNTIA_FIXTURE_RESULT:' in line]
        if len(lines)!=1:raise SystemExit('Fixture result missing; no credentials printed')
        fixtures.append(json.loads(lines[0]))
    # Import only after preparing the private local store; no production app configuration is loaded.
    from agntia_gestoria.storage import Database,canonical,now,uid
    from agntia_gestoria.models import CompanyCreate
    from cryptography.fernet import Fernet
    db=Database(state/'gestoria-data');owner=secrets.token_urlsafe(36);actors={};servers={};settings={'GESTORIA_OWNER_TOKEN':owner,'GESTORIA_DATA_DIR':str(db.root),'ODOO_ADAPTER_ENABLED':'true','ODOO_TEST_MODE':'true','ODOO_IDENTITY_MODE':'standalone','ODOO_REQUIRE_SCANNER':'false','ODOO_DOCUMENT_KEY':Fernet.generate_key().decode(),'ODOO_BRIDGE_SIGNING_KEY':(state/'secrets/bridge_signing_key').read_text().strip()}
    for i,fixture in enumerate(fixtures):
        cid=uid();territory='common' if i==0 else 'canarias';form='autonomo' if i==0 else 'sl'
        body=CompanyCreate(name='Agntia synthetic '+str(i+1),legal_form=form,tax_territory=territory,facts={'vat_status':'liable','vat_return_required':True,'vat_periodicity':'quarterly','irpf_payment_model':'130' if i==0 else 'none'})
        company={'id':cid,'revision':0,**body.model_dump(mode='json'),'created_at':now()}
        with db.transaction() as c:c.execute('INSERT INTO companies VALUES(?,?)',(cid,canonical(company)))
        fixture['gestoria_company_id']=cid;fixture['agent_token']=secrets.token_urlsafe(36);fixture['reviewer_token']=secrets.token_urlsafe(36)
        actors[fixture['agent_token']]={'id':'synthetic-agent-'+str(i),'role':'agent','companies':[cid]}
        actors[fixture['reviewer_token']]={'id':'synthetic-reviewer-'+str(i),'role':'reviewer','companies':[cid]}
        for label,role in [('operator','agent'),('viewer','viewer')]:
            token=secrets.token_urlsafe(36);fixture[label+'_token']=token;actors[token]={'id':'synthetic-'+label+'-'+str(i),'role':role,'companies':[cid]}
        envkey='ODOO_SYNTHETIC_KEY_'+str(i);settings[envkey]=fixture['api_key'];ref='synthetic-'+str(i);fixture['server_ref']=ref
        servers[ref]={'base_url':'http://127.0.0.1:'+os.getenv('AGNTIA_ODOO_PORT','8069'),'database':fixture['database'],'api_key_env':envkey,'gestoria_company_id':cid,'tenant_id':'standalone:'+cid,'odoo_company_id':fixture['company_id'],'expected_instance_id':fixture['instance_id'],'allowed_networks':['127.0.0.0/8','::1/128'],'allow_insecure_test':True,'write_enabled':True,'allowed_partner_ids':[fixture['partner_id']],'allowed_journal_ids':[fixture['journal_id']],'allowed_account_ids':[fixture['account_id']],'allowed_tax_ids':[fixture['tax_id']],'tax_mappings':{str(fixture['tax_id']):{'tax_kind':'iva' if i==0 else 'igic','rate':fixture['tax_rate']}}}
        # Synthetic fixtures exercise jurisdiction boundaries; they are not legal tax validation.
    settings['GESTORIA_ACTORS_JSON']=json.dumps(actors);settings['ODOO_SERVERS_JSON']=json.dumps(servers)
    (state/'run-env.json').write_text(json.dumps(settings,indent=2))
    (state/'fixtures.private.json').write_text(json.dumps({'owner_token':owner,'companies':fixtures},indent=2))
    container={**settings,'GESTORIA_DATA_DIR':'/data'};docker_servers=json.loads(settings['ODOO_SERVERS_JSON'])
    for server in docker_servers.values():server['base_url']='http://odoo:8069';server['allowed_networks']=[os.getenv('AGNTIA_LAB_SUBNET','172.30.241.0/24')]
    container['ODOO_SERVERS_JSON']=json.dumps(docker_servers)
    (state/'gestoria.env.local').write_text(''.join(key+'='+json.dumps(value)+'\n' for key,value in container.items()))
    print('Two synthetic DBs and isolated principals provisioned. Credentials saved privately; no tokens printed.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--state-dir',required=True);p.add_argument('--synthetic-lab',action='store_true',required=True);p.add_argument('--prepare',action='store_true');p.add_argument('--bootstrap',action='store_true');p.add_argument('--start-app',action='store_true');args=p.parse_args()
    if sum((args.prepare,args.bootstrap,args.start_app))!=1:p.error('Choose exactly one action')
    state=state_dir(args.state_dir,args.prepare)
    if args.prepare:prepare(state)
    elif args.bootstrap:bootstrap(state)
    else:compose(state,'--profile','app','up','-d','--build','gestoria','worker')


if __name__=='__main__':main()
