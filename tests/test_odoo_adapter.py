import base64
import copy
import hashlib
import json
import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import httpx
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from agntia_gestoria.app import create_app
from agntia_gestoria.auth import Actor
from agntia_gestoria.storage import Database,canonical,digest
from agntia_gestoria.integrations.contracts import ConnectionCreate,BindingValidation,PartnerChange,ApprovalRequest,CommitRequest,Money,OperationEnvelope
from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.registry import Server,load_server,resolve_target
from agntia_gestoria.integrations.migrations import migrate
from agntia_gestoria.integrations.odoo.adapter import Adapter
from agntia_gestoria.integrations.odoo.discovery import FIELDS
from agntia_gestoria.integrations.odoo.transport import Client,_FAILURES
from agntia_gestoria.integrations.odoo.mappers.invoice import invoice


class Provider:
    def __init__(self):
        self.calls=[];self.operations={};self.writes=0;self.timeout_once=False
        self.partners=[{'id':1,'company_id':[1,'Fixture'],'name':'Cliente fixture','vat':'ESB00000000','email':'fixture@example.invalid','country_id':[68,'Spain'],'is_company':True,'write_date':'2026-11-09 10:00:00'}]
        self.snapshot={'move':{'id':10,'company_id':1,'move_type':'out_invoice','state':'draft','currency':'EUR','invoice_date':'2026-04-10','amount_untaxed':'100.00','amount_tax':'21.00','amount_total':'121.00','partner_name':'Cliente fixture','fiscal_position_id':None,'cash_basis':False,'write_date':'2026-11-09 10:00:00'},'lines':[{'id':20,'move_id':10,'company_id':1,'display_type':'product','name':'Servicio fixture','quantity':'1','price_unit':'100','discount':'0','price_subtotal':'100.00','price_total':'121.00','taxes':[{'id':3,'company_id':1,'amount':'21.00','amount_type':'percent','type_tax_use':'sale','price_include':False,'children_tax_ids':[],'write_date':'2026-11-09 09:00:00'}]}]}
        self.info={'source_revision':'60657b50d171ddf84ab58717fdee5ac26031065b','enterprise_installed':False,'version':'19.0','bridge_version':'1.0','instance_id':'b'*32,'uid':4,'superuser':False,'settings_admin':False,'company_id':1,'company_vat':'ESB00000000','allowed_company_ids':[1],'read_access':{m:True for m in FIELDS},'write_access':{'res.partner':True,'account.move':True},'modules':{'base':'19.0','account':'19.0','l10n_es':'19.0'}}
    def call(self,model,method,payload=None):
        payload=payload or {};self.calls.append((model,method,copy.deepcopy(payload)))
        if method=='server_info':return copy.deepcopy(self.info)
        if method=='fields_get':return {k:{'type':'char'} for k in FIELDS[model]}
        if model=='res.partner' and method=='search_read':
            rows=copy.deepcopy(self.partners)
            for field,op,value in payload.get('domain',[]):
                if field=='id' and op=='>':rows=[r for r in rows if r['id']>value]
                if field=='id' and op=='=':rows=[r for r in rows if r['id']==value]
            return rows[:payload.get('limit',100)]
        if model=='account.move' and method=='search_read':
            return [{'id':10,'company_id':1,'state':self.snapshot['move']['state'],'move_type':self.snapshot['move']['move_type'],'write_date':self.snapshot['move']['write_date']}] if self.snapshot else []
        if method=='invoice_snapshots':return [copy.deepcopy(self.snapshot)] if self.snapshot else []
        if method=='preview_invoice':return {'base':'100.00','tax':'21.00','total':'121.00'}
        if method=='execute_approved':
            key=payload['operation_key']
            if key not in self.operations:
                self.writes+=1;kind=payload['payload']['kind'];self.operations[key]={'kind':kind,'remote_id':100+self.writes,'company_id':1,'request_hash':payload['request_hash'],'write_date':'2026-11-09 11:00:00'}
                if kind=='invoice_draft':self.operations[key].update(state='draft',totals={'base':'100.00','tax':'21.00','total':'121.00'})
            if self.timeout_once:self.timeout_once=False;raise IntegrationError('timeout','Synthetic uncertain write',504,True,True)
            return copy.deepcopy(self.operations[key])
        if method=='operation_status':return copy.deepcopy(self.operations.get(payload['operation_key'],False))
        if method=='attachment_metadata':return [{'id':7,'invoice_id':10,'name':'proof.pdf','size':20,'mimetype':'application/pdf'}]
        if method=='attachment_content':
            raw=b'%PDF-1.7\nsynthetic fixture'
            return {'id':7,'invoice_id':10,'company_id':1,'name':'../../proof.pdf','sha256':hashlib.sha256(raw).hexdigest(),'data':base64.b64encode(raw).decode()}
        raise AssertionError('Unexpected synthetic provider call '+model+'.'+method)


class AdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.provider=Provider()
        self.settings={'ODOO_ADAPTER_ENABLED':'true','ODOO_TEST_MODE':'true','ODOO_IDENTITY_MODE':'standalone','ODOO_BOT_KEY':'sentinel-api-key-not-for-production','ODOO_BRIDGE_SIGNING_KEY':'sentinel-signing-key-not-for-production-long','ODOO_REQUIRE_SCANNER':'false','ODOO_DOCUMENT_KEY':Fernet.generate_key().decode(),'GESTORIA_OWNER_TOKEN':'owner-fixture-token-12345','GESTORIA_ACTORS_JSON':json.dumps({'agent-fixture-token-12345':{'id':'bot','role':'agent','companies':['*']},'viewer-fixture-token-12345':{'id':'viewer','role':'viewer','companies':['*']}})}
        self.env=patch.dict(os.environ,self.settings);self.env.start()
        self.app=create_app(self.tmp.name);self.app.state.odoo_client_factory=lambda server:self.provider
        self.client=TestClient(self.app);self.owner={'Authorization':'Bearer owner-fixture-token-12345'};self.agent={'Authorization':'Bearer agent-fixture-token-12345'};self.viewer={'Authorization':'Bearer viewer-fixture-token-12345'}
        self.company=self.client.post('/api/companies',headers=self.owner,json={'name':'Fixture autonomo','legal_form':'autonomo','tax_territory':'common','nif':'ESB00000000','facts':{'vat_status':'liable','vat_return_required':True,'vat_periodicity':'quarterly','irpf_payment_model':'130'}}).json();self.cid=self.company['id'];self.root='/api/companies/'+self.cid;self.api=self.root+'/integrations/odoo'
        self.server={'base_url':'http://localhost:8069','database':'agntia_test_a','api_key_env':'ODOO_BOT_KEY','gestoria_company_id':self.cid,'tenant_id':'standalone:'+self.cid,'odoo_company_id':1,'expected_instance_id':'b'*32,'allowed_networks':['127.0.0.0/8'],'allow_insecure_test':True,'write_enabled':True,'allowed_partner_ids':[1],'allowed_journal_ids':[1],'allowed_account_ids':[1],'allowed_tax_ids':[3],'tax_mappings':{'3':{'tax_kind':'iva','rate':'21'}}}
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':self.server})
        self.adapter=Adapter(self.app.state.db,lambda server:self.provider);self.actor=Actor('owner','owner',('*',));self.bot=Actor('bot','agent',('*',))
        c=self.client.post(self.api+'/connections',headers=self.owner,json={'server_ref':'fixture'});self.assertEqual(c.status_code,200,c.text)
        v=self.client.post(self.api+'/connections/validate',headers=self.owner,json={'revision':0});self.assertEqual(v.status_code,200,v.text)
    def tearDown(self):self.client.close();self.env.stop();self.tmp.cleanup()
    def import_invoice(self,key='invoice-import'):
        result=self.adapter.preview(self.bot,self.cid,'invoices',True,'correlation')
        return self.adapter.import_stages(self.bot,self.cid,result['staging_ids'],key,'correlation')
    def partner_proposal(self):
        r=self.client.post(self.api+'/partners/dry-run',headers=self.agent,json={'name':'Nuevo contacto fixture'})
        self.assertEqual(r.status_code,200,r.text);return r.json()
    def approved_body(self,proposal,key='commit-key'):
        r=self.client.post(self.api+'/proposals/'+proposal['id']+'/approve',headers=self.owner,json={'revision':0,'proposal_hash':proposal['proposal_hash'],'notes':'Synthetic human review'})
        self.assertEqual(r.status_code,200,r.text)
        return {'proposal_id':proposal['id'],'approval_id':r.json()['id'],'expected_revision':0,'idempotency_key':key}

    def test_import_replay_and_no_inferred_approval(self):
        first=self.import_invoice();self.assertEqual(first['imported'],1)
        records=self.client.get(self.root+'/tax-records',headers=self.owner).json();self.assertEqual(len(records),1)
        record=records[0];self.assertEqual(record['status'],'unverified');self.assertIsNone(record['deductible_tax_amount']);self.assertEqual(record['category'],'other')
        second=self.import_invoice('other-import-key');self.assertEqual(second['unchanged'],1)
        self.assertEqual(len(self.client.get(self.root+'/tax-records',headers=self.owner).json()),1)
        serialized=json.dumps(self.client.get(self.root+'/export',headers=self.owner).json())
        self.assertNotIn(self.settings['ODOO_BOT_KEY'],serialized);self.assertNotIn(self.server['database'],serialized)

    def test_mapping_blocked_and_source_conflict_stales_calculation(self):
        result=self.import_invoice();record_id=result['local_ids'][0]
        self.provider.snapshot['move'].update(amount_untaxed='200.00',amount_tax='42.00',amount_total='242.00',write_date='2026-11-09 12:00:00')
        self.provider.snapshot['lines'][0].update(price_subtotal='200.00',price_total='242.00')
        self.adapter.preview(self.bot,self.cid,'invoices',True,'conflict')
        conflicts=self.client.get(self.api+'/conflicts',headers=self.owner).json();self.assertEqual(len(conflicts),1)
        records=self.client.get(self.root+'/tax-records',headers=self.owner).json();self.assertEqual(len(records),2)
        original=next(r for r in records if r['id']==record_id);self.assertEqual(original['base_amount'],'100.00')
        changed=next(r for r in records if r['id']!=record_id);self.assertEqual(changed['kind'],'adjustment')
        self.assertEqual(self.client.post(self.api+'/conflicts/'+conflicts[0]['id']+'/resolve',headers=self.agent,json={'revision':0,'decision':'keep_local','notes':'Cannot approve'}).status_code,403)
        resolved=self.client.post(self.api+'/conflicts/'+conflicts[0]['id']+'/resolve',headers=self.owner,json={'revision':0,'decision':'keep_local','notes':'Original evidence retained after review'})
        self.assertEqual(resolved.status_code,200,resolved.text)

    def test_uncertain_write_is_reconciled_without_second_create(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal);self.provider.timeout_once=True
        r=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body)
        self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['status'],'reconciliation_required')
        replay=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body)
        self.assertEqual(replay.json()['status'],'reconciliation_required');self.assertEqual(self.provider.writes,1)
        final=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':body['idempotency_key']})
        self.assertEqual(final.status_code,200,final.text);self.assertEqual(final.json()['status'],'succeeded');self.assertEqual(self.provider.writes,1)
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).json()['remote_id'],final.json()['remote_id'])

    def test_agent_cannot_approve_or_commit(self):
        p=self.partner_proposal();body=self.approved_body(p)
        self.assertEqual(self.client.post(self.api+'/proposals/'+p['id']+'/approve',headers=self.agent,json={'revision':0,'proposal_hash':p['proposal_hash'],'notes':'Bot approval denied'}).status_code,403)
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.agent,json=body).status_code,403)
        self.assertEqual(self.client.post(self.api+'/imports/preview',headers=self.viewer,json={'resource':'invoices','full':True,'idempotency_key':'viewer-key'}).status_code,403)
        self.assertEqual(self.provider.writes,0)

    def test_jobs_are_scoped_idempotent_and_revalidate_revocation(self):
        request={'resource':'invoices','full':True,'idempotency_key':'preview-job-key'}
        r=self.client.post(self.api+'/imports/preview',headers=self.agent,json=request);self.assertEqual(r.status_code,202,r.text)
        self.assertEqual(self.client.post(self.api+'/imports/preview',headers=self.agent,json=request).json()['job_id'],r.json()['job_id'])
        request['resource']='partners';self.assertEqual(self.client.post(self.api+'/imports/preview',headers=self.agent,json=request).status_code,409)
        done=self.adapter.run_one();self.assertEqual(done['state'],'succeeded',done)
        self.assertEqual(self.client.get(self.api+'/jobs/'+r.json()['job_id'],headers=self.owner).json()['state'],'succeeded')
        request['idempotency_key']='revoked-job';self.client.post(self.api+'/imports/preview',headers=self.agent,json=request)
        os.environ['GESTORIA_ACTORS_JSON']='{}'
        done=self.adapter.run_one();self.assertNotEqual(done['state'],'succeeded')

    def test_encrypted_document_and_human_classification(self):
        result=self.import_invoice();rid=result['local_ids'][0]
        doc=self.client.post(self.api+'/invoices/10/attachments/download',headers=self.owner,json={'attachment_id':7})
        self.assertEqual(doc.status_code,200,doc.text);d=doc.json();self.assertEqual(d['name'],'proof.pdf')
        path=Path(self.tmp.name)/'documents'/self.cid/d['stored_name'];self.assertNotIn(b'%PDF-',path.read_bytes())
        downloaded=self.client.get(self.root+'/documents/'+d['id']+'/download',headers=self.owner)
        self.assertTrue(downloaded.content.startswith(b'%PDF-'),downloaded.text)
        classification={'revision':0,'operation_date':'2026-04-10','tax_kind':'iva','category':'ordinary','vat_treatment':'domestic_current','tax_rate':'21','deductible_tax_amount':None,'deductible_irpf_amount':None,'document_ids':[d['id']],'notes':'Source and fiscal date confirmed against sufficient original evidence','issued_evidence_confirmed':True}
        self.assertEqual(self.client.post(self.api+'/records/'+rid+'/classification',headers=self.agent,json=classification).status_code,403)
        classified=self.client.post(self.api+'/records/'+rid+'/classification',headers=self.owner,json=classification)
        self.assertEqual(classified.status_code,200,classified.text);self.assertEqual(classified.json()['status'],'unverified')
        reviewed=self.client.post(self.root+'/tax-records/'+rid+'/review',headers=self.owner,json={'revision':1,'notes':'Human review of original evidence completed'})
        self.assertEqual(reviewed.status_code,200,reviewed.text)
        calc=self.client.post(self.root+'/tax-calculations',headers=self.agent,json={'model':'303','year':2026,'period':'2T','regime':'iva_general_domestic','confirmed_standard_scope':True})
        self.assertEqual(calc.status_code,200,calc.text);self.assertEqual(calc.json()['boxes']['71'],'21.00')
        report=self.client.post(self.root+'/reports',headers=self.agent,json={'year':2026});self.assertEqual(report.status_code,200)
        integrity=self.client.get(self.api+'/audit-integrity',headers=self.owner).json();self.assertTrue(integrity['valid'],integrity)

    def test_cross_company_denied_before_provider_call(self):
        other=self.client.post('/api/companies',headers=self.owner,json={'name':'Other company','legal_form':'sl'}).json()['id']
        before=len(self.provider.calls)
        result=self.client.post('/api/companies/'+other+'/integrations/odoo/connections',headers=self.owner,json={'server_ref':'fixture'})
        self.assertEqual(result.status_code,404,result.text);self.assertEqual(len(self.provider.calls),before)
        with patch.dict(os.environ,{'GESTORIA_ACTORS_JSON':json.dumps({'scoped-fixture-token-12345':{'id':'scoped','role':'agent','companies':[other]}})}):
            self.assertEqual(self.client.get(self.api+'/health',headers={'Authorization':'Bearer scoped-fixture-token-12345'}).status_code,404)

    def test_schema_rejects_payload_context_and_server_url(self):
        before=len(self.provider.calls)
        r=self.client.post(self.api+'/partners/dry-run',headers=self.agent,json={'name':'Fixture','context':{'allowed_company_ids':[2]}})
        self.assertEqual(r.status_code,422);self.assertEqual(len(self.provider.calls),before)
        self.assertEqual(self.client.post(self.api+'/connections',headers=self.owner,json={'server_ref':'fixture','base_url':'http://169.254.169.254'}).status_code,422)

    def test_discovery_denies_wrong_database_and_admin(self):
        self.provider.info['instance_id']='c'*32
        r=self.client.post(self.api+'/connections/validate',headers=self.owner,json={'revision':1})
        self.assertEqual(r.status_code,424,r.text)
        self.assertEqual(self.client.get(self.api+'/health',headers=self.owner).json()['state'],'degraded')


class PureTests(unittest.TestCase):
    def setUp(self):_FAILURES.clear()
    def server(self):
        return Server(base_url='https://odoo.example.invalid',database='agntia_test_a',api_key_env='TEST_ODOO_KEY',gestoria_company_id='a'*32,tenant_id='standalone:'+'a'*32,odoo_company_id=1,expected_instance_id='b'*32,allowed_networks=['192.0.2.0/24'])
    def test_transport_is_pinned_and_no_secret_error_payload(self):
        server=self.server();captured=[]
        def handle(req):
            captured.append(req)
            return httpx.Response(403,json={'debug':'secret TRACE sentinel-private'})
        with patch.dict(os.environ,{'TEST_ODOO_KEY':'sentinel-secret-api-key'}):
            client=Client(server,transport=httpx.MockTransport(handle),resolver=lambda h,p:['192.0.2.10'],sleep=lambda _:None)
            with self.assertRaises(IntegrationError) as error:client.call('res.partner','search_read',{'fields':['id'],'domain':[]})
            self.assertNotIn('sentinel',json.dumps(error.exception.public()));self.assertNotIn('TRACE',str(error.exception))
            self.assertEqual(captured[0].url.host,'192.0.2.10');self.assertEqual(captured[0].headers['Host'],'odoo.example.invalid');self.assertEqual(captured[0].extensions['sni_hostname'],'odoo.example.invalid')
            self.assertEqual(json.loads(captured[0].content)['context']['allowed_company_ids'],[1])
            with self.assertRaises(IntegrationError):client.call('account.move','action_post',{'ids':[1]})
            with self.assertRaises(IntegrationError):client.call('res.partner','search_read',{'context':{}})
            self.assertEqual(len(captured),1)
    def test_transport_timeout_write_never_retries(self):
        server=self.server();server.write_enabled=True;count=[]
        def timeout(req):count.append(req);raise httpx.ReadTimeout('sentinel secret')
        with patch.dict(os.environ,{'TEST_ODOO_KEY':'sentinel-secret-api-key'}):
            client=Client(server,httpx.MockTransport(timeout),lambda h,p:['192.0.2.1'],lambda _:None)
            with self.assertRaises(IntegrationError) as error:client.call('agntia.bridge','execute_approved',{})
            self.assertTrue(error.exception.uncertain);self.assertEqual(len(count),1)
    def test_ssrf_and_invalid_money(self):
        server=self.server()
        for address in ['169.254.169.254','127.0.0.1','::ffff:169.254.169.254','0.0.0.0']:
            with self.assertRaises(IntegrationError):resolve_target(server,lambda h,p:[address])
        for value in ['NaN','Infinity',1.2]:
            with self.assertRaises(ValueError):Money(amount=value)
        self.assertEqual(Money(amount='100.01').model_dump(mode='json')['amount'],'100.01')
    def test_mapping_rounding_refund_and_ambiguity(self):
        p=Provider();server=self.server();server.tax_mappings={'3':{'tax_kind':'iva','rate':'21'}}
        mapped=invoice(p.snapshot,server,'d'*32);self.assertFalse(mapped['blocked'])
        p.snapshot['move']['move_type']='out_refund';mapped=invoice(p.snapshot,server,'d'*32);self.assertEqual(mapped['facts'][0]['record']['base_amount'],'-100.00')
        p.snapshot['move']['currency']='USD';self.assertTrue(invoice(p.snapshot,server,'d'*32)['blocked'])
        p.snapshot['move']['currency']='EUR';p.snapshot['lines'][0]['taxes'].append(copy.deepcopy(p.snapshot['lines'][0]['taxes'][0]));self.assertTrue(invoice(p.snapshot,server,'d'*32)['blocked'])
    def test_migration_preserves_core_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            db=Database(folder)
            with db.transaction() as c:c.execute('INSERT INTO companies VALUES(?,?)',('a'*32,canonical({'id':'a'*32,'name':'Existing'})))
            backup=migrate(db);self.assertTrue(backup.is_file());self.assertIsNone(migrate(db))
            with db.connection() as c:self.assertEqual(db.company(c,'a'*32)['name'],'Existing');self.assertEqual(c.execute('SELECT count(*) FROM integration_migrations').fetchone()[0],1)


class AdditionalAdapterTests(AdapterTest):
    # Inherit the end-to-end fixture, but only run newly defined cases in this class.
    def test_new_key_cannot_execute_same_proposal_twice(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'once-key')
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).json()['status'],'succeeded')
        body['idempotency_key']='different-key'
        response=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body)
        self.assertEqual(response.status_code,409,response.text);self.assertEqual(self.provider.writes,1)
    def test_proposal_tamper_fails_before_remote_write(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal)
        with self.app.state.db.transaction() as c:
            raw=json.loads(c.execute('SELECT body FROM integration_proposals WHERE id=?',(proposal['id'],)).fetchone()['body']);raw['payload']['values']['name']='Tampered'
            c.execute('UPDATE integration_proposals SET body=? WHERE id=?',(canonical(raw),proposal['id']))
        response=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body)
        self.assertEqual(response.status_code,409,response.text);self.assertEqual(self.provider.writes,0)
    def test_binding_cannot_be_silently_rotated_to_new_instance(self):
        value=copy.deepcopy(self.server);value['expected_instance_id']='c'*32;self.provider.info['instance_id']='c'*32
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':value});before=len(self.provider.calls)
        result=self.client.post(self.api+'/connections/validate',headers=self.owner,json={'revision':1})
        self.assertEqual(result.status_code,409,result.text);self.assertEqual(len(self.provider.calls),before)
        self.assertEqual(self.client.post(self.api+'/connections/disable',headers=self.owner,json={'revision':1}).status_code,200)
    def test_expired_capabilities_and_write_configuration_fail_closed(self):
        with self.app.state.db.transaction() as c:
            row=c.execute('SELECT body FROM provider_connections WHERE company_id=?',(self.cid,)).fetchone();conn=json.loads(row['body']);conn['report']['expires_at']='2000-01-01T00:00:00+00:00';self.adapter.save_connection(c,conn)
        before=len(self.provider.calls);result=self.client.post(self.api+'/imports/preview',headers=self.agent,json={'resource':'invoices','full':False,'idempotency_key':'expired'})
        self.assertEqual(result.status_code,424,result.text);self.assertEqual(len(self.provider.calls),before)
    def test_preview_source_change_blocks_acceptance(self):
        preview=self.adapter.preview(self.bot,self.cid,'invoices',True,'preview-change')
        self.provider.snapshot['move']['write_date']='2026-11-09 13:00:00'
        with self.assertRaises(IntegrationError):self.adapter.import_stages(self.bot,self.cid,preview['staging_ids'],'stale-import','preview-change')
        self.assertEqual(self.client.get(self.root+'/tax-records',headers=self.owner).json(),[])
    def test_conflict_acknowledgement_does_not_reopen_identical_change(self):
        self.import_invoice();self.provider.snapshot['move']['write_date']='2026-11-09 13:00:00'
        self.adapter.preview(self.bot,self.cid,'invoices',True,'change')
        conflict=self.client.get(self.api+'/conflicts',headers=self.owner).json()[0]
        self.client.post(self.api+'/conflicts/'+conflict['id']+'/resolve',headers=self.owner,json={'revision':0,'decision':'keep_local','notes':'Explicit human decision to retain original evidence'})
        self.adapter.preview(self.bot,self.cid,'invoices',True,'replay')
        conflicts=self.client.get(self.api+'/conflicts',headers=self.owner).json();self.assertEqual(len(conflicts),1);self.assertEqual(conflicts[0]['state'],'resolved')
    def test_event_delivery_replay_and_content_integrity(self):
        events=self.client.get(self.api+'/events',headers=self.owner).json();self.assertTrue(events)
        body={'event_ids':[events[0]['id']]}
        for _ in range(2):self.assertEqual(self.client.post(self.api+'/events/ack',headers=self.agent,json=body).status_code,200)
        self.assertTrue(self.client.get(self.api+'/audit-integrity',headers=self.owner).json()['valid'])
        with self.app.state.db.transaction() as c:
            changed=copy.deepcopy(events[0]);changed['payload']['tampered']=True;c.execute('UPDATE integration_outbox SET body=? WHERE id=?',(canonical(changed),changed['id']))
        self.assertFalse(self.client.get(self.api+'/audit-integrity',headers=self.owner).json()['valid'])
    def test_invoice_projection_is_draft_only_and_matches_hash(self):
        draft=self.client.post(self.root+'/invoice-drafts',headers=self.owner,json={'customer_name':'Fixture customer','operation_date':'2026-04-10','tax_kind':'iva','withholding_rate':'0','lines':[{'description':'Service','quantity':'1','unit_price':'100','tax_rate':'21'}]}).json()
        projection=self.client.get(self.api+'/invoice-drafts/'+draft['id']+'/projection-input',headers=self.owner).json()
        payload={'invoice_draft_id':draft['id'],'partner_id':1,'journal_id':1,'account_id':1,'tax_ids':[3],'expected_draft_hash':projection['source_hash']}
        response=self.client.post(self.api+'/invoice-drafts/dry-run',headers=self.agent,json=payload);self.assertEqual(response.status_code,200,response.text)
        body=self.approved_body(response.json(),'draft-projection');commit=self.client.post(self.api+'/invoice-drafts/commit',headers=self.owner,json=body)
        self.assertEqual(commit.status_code,200,commit.text);self.assertEqual(commit.json()['remote_state'],'draft')
        self.assertEqual(self.provider.writes,1)
    def test_scanner_is_required_by_default(self):
        self.import_invoice()
        with patch.dict(os.environ,{'ODOO_REQUIRE_SCANNER':'true'}):
            response=self.client.post(self.api+'/invoices/10/attachments/download',headers=self.owner,json={'attachment_id':7})
            self.assertEqual(response.status_code,424,response.text)
    def test_integrated_tenant_claim_is_server_owned(self):
        scope={'owner':{'tenant_id':'tenant-expected','companies':[self.cid],'capabilities':['health']}}
        with patch.dict(os.environ,{'ODOO_IDENTITY_MODE':'integrated','ODOO_ACTOR_SCOPES_JSON':json.dumps(scope)}):
            self.assertEqual(self.client.get(self.api+'/health',headers=self.owner).status_code,404)
    def test_expired_job_lease_is_recovered(self):
        request={'resource':'partners','full':True,'idempotency_key':'lease-recovery'}
        job=self.client.post(self.api+'/imports/preview',headers=self.agent,json=request).json()['job_id']
        with self.app.state.db.transaction() as c:c.execute("UPDATE sync_jobs SET state='running',lease_owner='dead-worker',lease_until='2000-01-01T00:00:00+00:00' WHERE id=?",(job,))
        done=self.adapter.run_one();self.assertEqual(done['state'],'succeeded',done)

# unittest normally inherits parent test methods. Avoid counting the same scenarios twice.
for _name in list(AdapterTest.__dict__):
    if _name.startswith('test_') and _name not in AdditionalAdapterTests.__dict__:setattr(AdditionalAdapterTests,_name,None)


class AdditionalPureTests(unittest.TestCase):
    def test_migration_failure_rolls_back_schema(self):
        from agntia_gestoria.integrations import migrations
        with tempfile.TemporaryDirectory() as folder:
            db=Database(folder)
            with patch.object(migrations,'DDL',[*migrations.DDL,'INVALID SQL SENTINEL']):
                with self.assertRaises(Exception):migrations.migrate(db)
            with db.connection() as c:
                self.assertIsNone(c.execute("SELECT name FROM sqlite_master WHERE name='provider_connections'").fetchone())
                self.assertIsNotNone(c.execute("SELECT name FROM sqlite_master WHERE name='companies'").fetchone())
    def test_more_than_thousand_partners_keyset_pagination(self):
        from agntia_gestoria.integrations.odoo.reads import read_partners
        provider=Provider();provider.partners=[{**provider.partners[0],'id':i,'name':'Same fixture name'} for i in range(1,1102)]
        server=Server(base_url='https://fixture.invalid',database='agntia_test_a',api_key_env='TEST_ODOO_KEY',gestoria_company_id='a'*32,tenant_id='standalone:'+'a'*32,odoo_company_id=1,expected_instance_id='b'*32,allowed_networks=['192.0.2.0/24'])
        rows=[row for page in read_partners(provider,server) for row in page];self.assertEqual(len(rows),1101);self.assertEqual(len(set(r['external_id'] for r in rows)),1101)
    def test_redirect_and_oversize_fail_without_echoing_payload(self):
        server=PureTests().server();server.max_response_bytes=1024
        with patch.dict(os.environ,{'TEST_ODOO_KEY':'sentinel-secret-api-key'}):
            for status,headers,content in [(302,{'Location':'http://169.254.169.254'},b'private'),(200,{},b'x'*2000)]:
                client=Client(server,httpx.MockTransport(lambda req:httpx.Response(status,headers=headers,content=content)),lambda h,p:['192.0.2.1'],lambda _:None)
                with self.assertRaises(IntegrationError) as error:client.call('res.partner','search_read',{})
                self.assertFalse(error.exception.retryable);self.assertNotIn('private',str(error.exception))

if __name__=='__main__':unittest.main()
