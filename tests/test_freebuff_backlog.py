"""Regresiones del encargo Freebuff del 10/11/2026 (82 puntos del handoff).

Cada test declara el ID de tarea del documento `docs/handoff-freebuff-2026-11-10.md`.
Todos usan datos sintéticos y dobles: un PASS aquí no es un PASS de laboratorio
Odoo real. Lo que necesita instancia, Docker o el runtime de Agente queda
BLOCKED y vive en `pendientes.md`.
"""
import copy
import hashlib
import hmac
import json
import os
import re
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch

import httpx

import test_odoo_adapter as fixtures
from agntia_gestoria.integrations.contracts import (CapabilityReport,CommitRequest,
                                                    Conflict,ImportPreview,OperationEnvelope,
                                                    OperationResult,SyncCursor,SyncJob,
                                                    ExternalObjectLink)
from agntia_gestoria.integrations.contracts_export import export
from agntia_gestoria.integrations.errors import CONTRACT,IntegrationError
from agntia_gestoria.integrations.odoo.reads import read_partners
from agntia_gestoria.integrations.odoo.transport import Client
from agntia_gestoria.integrations.registry import Server,load_server
from agntia_gestoria.integrations.retention import classify,retention_days,retention_window
from agntia_gestoria.storage import canonical,digest


class Provider(fixtures.Provider):
    """Doble del bridge con dos fallos que el fixture base no modela."""

    def __init__(self):
        super().__init__();self.timeout_before=0;self.status_error=None

    def call(self,model,method,payload=None):
        if method=='execute_approved' and self.timeout_before:
            self.timeout_before-=1
            self.calls.append((model,method,copy.deepcopy(payload or {})))
            raise IntegrationError('timeout','Synthetic uncertain write',504,True,True)
        if method=='operation_status' and self.status_error:
            error=self.status_error;self.status_error=None;raise error
        return super().call(model,method,payload)


class BacklogBase(unittest.TestCase):
    partner_proposal=fixtures.AdapterTest.partner_proposal
    approved_body=fixtures.AdapterTest.approved_body
    import_invoice=fixtures.AdapterTest.import_invoice

    def setUp(self):
        fixtures.AdapterTest.setUp(self)
        self.provider=Provider();self.app.state.odoo_client_factory=lambda server:self.provider

    def tearDown(self):
        fixtures.AdapterTest.tearDown(self)

    def rotate_server(self,overrides=None):
        value={**self.server,**(overrides or {})}
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':value})
        return value

    def rehash_connection(self,value):
        with self.app.state.db.transaction() as c:
            row=c.execute('SELECT body FROM provider_connections WHERE company_id=?',(self.cid,)).fetchone()
            connection=json.loads(row['body'])
            connection['configuration_hash']=digest(Server.model_validate(value).model_dump(mode='json'))
            self.adapter.save_connection(c,connection)

    def ledger(self,key):
        with self.app.state.db.connection() as c:
            row=c.execute("SELECT state,body FROM idempotency_keys WHERE company_id=? AND operation='write' AND key=?",(self.cid,key)).fetchone()
        return row['state'],json.loads(row['body'])


class SnapshotArgumentTests(BacklogBase):
    def test_01_bridge_receives_invoice_ids_and_never_ids(self):
        self.import_invoice('invoice-ids-import')
        snapshots=[p for _,method,p in self.provider.calls if method=='invoice_snapshots']
        self.assertTrue(snapshots)
        for payload in snapshots:
            self.assertEqual(set(payload),{'company_id','invoice_ids'})
            self.assertNotIn('ids',payload)
            self.assertEqual(payload['invoice_ids'],[10])
        # Vista previa y relectura antes de confirmar usan la misma forma de argumento.
        self.assertEqual(len(snapshots),2)


class GenericWriteTests(unittest.TestCase):
    def test_04_generic_orm_writes_are_rejected_before_http(self):
        server=fixtures.PureTests().server();server.write_enabled=True
        requests=[]
        def handle(request):
            requests.append(request);return httpx.Response(200,json=[])
        with patch.dict(os.environ,{'TEST_ODOO_KEY':'sentinel-secret-api-key'}):
            client=Client(server,httpx.MockTransport(handle),lambda h,p:['192.0.2.1'],lambda _:None)
            for model,method in [('res.partner','write'),('res.partner','create'),('account.move','action_post'),('account.move','write')]:
                with self.assertRaises(IntegrationError) as error:client.call(model,method,{'ids':[1],'vals':{'name':'Synthetic'}})
                self.assertEqual(error.exception.code,'forbidden')
        self.assertEqual(requests,[])


class RoleMatrixTests(BacklogBase):
    def test_12_role_matrix_positive_and_negative(self):
        tokens={'owner':'owner-fixture-token-12345','agent':'agent-fixture-token-12345',
                'viewer':'viewer-fixture-token-12345','reviewer':'reviewer-fixture-token-12345'}
        actors={'agent-fixture-token-12345':{'id':'bot','role':'agent','companies':['*']},
                'viewer-fixture-token-12345':{'id':'viewer','role':'viewer','companies':['*']},
                'reviewer-fixture-token-12345':{'id':'reviewer','role':'reviewer','companies':['*']}}
        headers={role:{'Authorization':'Bearer '+token} for role,token in tokens.items()}
        with patch.dict(os.environ,{'GESTORIA_ACTORS_JSON':json.dumps(actors)}):
            for role in tokens:
                self.assertEqual(self.client.get(self.api+'/health',headers=headers[role]).status_code,200,role)
                self.assertEqual(self.client.get(self.api+'/conflicts',headers=headers[role]).status_code,200,role)
            for role,expected in (('owner',202),('reviewer',202),('agent',202),('viewer',403)):
                body={'resource':'partners','full':True,'idempotency_key':'matrix-preview-'+role}
                self.assertEqual(self.client.post(self.api+'/imports/preview',headers=headers[role],json=body).status_code,expected,role)
            for role,expected in (('owner',200),('reviewer',200),('agent',200),('viewer',403)):
                response=self.client.post(self.api+'/partners/dry-run',headers=headers[role],json={'name':'Fixture matrix '+role})
                self.assertEqual(response.status_code,expected,role)
            for role,expected in (('owner',200),('reviewer',200),('agent',403),('viewer',403)):
                proposal=self.partner_proposal()
                response=self.client.post(self.api+'/proposals/'+proposal['id']+'/approve',headers=headers[role],
                                          json={'revision':0,'proposal_hash':proposal['proposal_hash'],'notes':'Synthetic matrix review'})
                self.assertEqual(response.status_code,expected,role)
            for role,expected in (('agent',403),('viewer',403)):
                proposal=self.partner_proposal()
                self.assertEqual(self.client.post(self.api+'/partners/commit',headers=headers[role],json=self.approved_body(proposal)).status_code,expected,role)
            proposal=self.partner_proposal();body=self.approved_body(proposal,'matrix-commit-reviewer')
            self.assertEqual(self.client.post(self.api+'/partners/commit',headers=headers['reviewer'],json=body).status_code,200)
        self.assertEqual(self.provider.writes,1)


class ScopeCrossingTests(BacklogBase):
    def test_13_second_binding_to_same_instance_needs_explicit_multi_company(self):
        # Otro tenant sobre la misma instancia/base se rechaza siempre.
        other={**self.server,'gestoria_company_id':'c'*32,'tenant_id':'standalone:'+'c'*32,'allow_multi_company':True}
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':{**self.server,'allow_multi_company':True},'sibling':other})
        with self.assertRaises(IntegrationError) as error:load_server('fixture')
        self.assertEqual(error.exception.code,'configuration')
        # Mismo tenant y compañías hermanas: solo con multiempresa explícita en ambos bindings.
        sibling={**self.server,'gestoria_company_id':'c'*32,'allow_multi_company':True}
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':{**self.server,'allow_multi_company':True},'sibling':sibling})
        self.assertTrue(load_server('fixture').allow_multi_company)
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':{**self.server,'allow_multi_company':False},'sibling':sibling})
        with self.assertRaises(IntegrationError):load_server('fixture')
        os.environ['ODOO_SERVERS_JSON']=json.dumps({'fixture':self.server})

    def test_14_shared_contact_is_rejected_instead_of_silently_imported(self):
        self.provider.partners[0]['company_id']=False
        with self.assertRaises(IntegrationError) as error:self.adapter.preview(self.bot,self.cid,'partners',True,'shared-contact')
        self.assertEqual(error.exception.code,'scope_violation')
        self.assertEqual(self.client.get(self.api+'/staging',headers=self.owner).json(),[])

    def test_15_company_hierarchy_does_not_widen_the_binding(self):
        self.provider.partners[0]['company_id']=[2,'Filial sintética']
        with self.assertRaises(IntegrationError) as error:self.adapter.preview(self.bot,self.cid,'partners',True,'hierarchy')
        self.assertEqual(error.exception.code,'scope_violation')

    def test_16_scope_matrix_blocks_before_http(self):
        cases=[('instancia',{'expected_instance_id':'c'*32}),
               ('empresa remota',{'odoo_company_id':2}),
               ('base de datos',{'database':'agntia_test_b'}),
               ('mapeo fiscal',{'tax_mappings':{'3':{'tax_kind':'iva','rate':'10'}}})]
        for label,overrides in cases:
            self.rotate_server(overrides);before=len(self.provider.calls)
            with self.assertRaises(IntegrationError) as error:self.adapter.preview(self.bot,self.cid,'partners',True,'cross-'+label)
            self.assertIn(error.exception.code,('configuration_changed','not_found'),label)
            self.assertEqual(len(self.provider.calls),before,label)
            self.rotate_server(None)
        # Una credencial ausente se detecta en el transporte, nunca por un doble.
        missing={**self.server,'api_key_env':'ODOO_MISSING_KEY'}
        requests=[]
        with self.assertRaises(IntegrationError) as error:
            Client(Server.model_validate(missing),httpx.MockTransport(lambda r:(requests.append(r) or httpx.Response(200,json=[]))),lambda h,p:['127.0.0.1'],lambda _:None).call('res.partner','search_read',{'fields':['id'],'domain':[]})
        self.assertEqual(error.exception.code,'not_configured')
        self.assertEqual(requests,[])


class JobRotationTests(BacklogBase):
    def test_17_rotation_with_queued_job_fails_closed(self):
        request={'resource':'partners','full':True,'idempotency_key':'rotation-job'}
        self.assertEqual(self.client.post(self.api+'/imports/preview',headers=self.agent,json=request).status_code,202)
        self.rotate_server({'tax_mappings':{'3':{'tax_kind':'iva','rate':'10'}}})
        done=self.adapter.run_one()
        self.assertEqual(done['state'],'failed',done)
        self.assertEqual(done['error']['code'],'configuration_changed')
        self.assertEqual(self.client.get(self.api+'/jobs/'+done['job_id'],headers=self.owner).json()['state'],'failed')
        self.rotate_server(None)


class ApprovalTests(BacklogBase):
    def test_18_changes_after_approval_invalidate_it(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'stale-config')
        self.rotate_server({'tax_mappings':{'3':{'tax_kind':'iva','rate':'10'}}})
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).status_code,409)
        self.rotate_server(None)

        proposal=self.partner_proposal();body=self.approved_body(proposal,'expired-approval')
        with self.app.state.db.transaction() as c:
            approval=json.loads(c.execute('SELECT body FROM integration_approvals WHERE id=?',(body['approval_id'],)).fetchone()['body'])
            approval['expires_at']='2000-01-01T00:00:00+00:00'
            c.execute('UPDATE integration_approvals SET body=? WHERE id=?',(canonical(approval),approval['id']))
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).status_code,403)

        proposal=self.partner_proposal();body=self.approved_body(proposal,'stale-connection')
        with self.app.state.db.transaction() as c:
            connection=self.adapter._connection(c,self.cid,json.loads(c.execute('SELECT body FROM provider_connections WHERE company_id=?',(self.cid,)).fetchone()['body'])['id'])
            connection.update(revision=connection['revision']+1);self.adapter.save_connection(c,connection)
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).status_code,409)
        self.assertEqual(self.provider.writes,0)

    def test_19_signed_approval_binds_payload_approver_and_instance(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'signed-proof')
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).status_code,200)
        authorization=next(p for _,method,p in self.provider.calls if method=='execute_approved')['authorization']
        claims=authorization['claims']
        self.assertEqual(set(claims),{'instance_id','company_id','operation_key','request_hash','approval_id','approved_by','expires_at'})
        self.assertEqual(claims['approval_id'],body['approval_id'])
        self.assertEqual(claims['approved_by'],'owner')
        self.assertEqual(claims['instance_id'],self.server['expected_instance_id'])
        self.assertLessEqual(claims['expires_at'],int(time.time())+300)
        key=self.settings['ODOO_BRIDGE_SIGNING_KEY'].encode()
        self.assertEqual(authorization['signature'],hmac.new(key,canonical(claims).encode(),hashlib.sha256).hexdigest())
        for change in ({'request_hash':'0'*64},{'approved_by':'agent'},{'instance_id':'c'*32},{'operation_key':'f'*64}):
            self.assertNotEqual(authorization['signature'],hmac.new(key,canonical({**claims,**change}).encode(),hashlib.sha256).hexdigest())
        self.assertEqual(self.provider.writes,1)
        source=(Path(__file__).resolve().parents[1]/'infra/odoo/addons/agntia_bridge/models/bridge.py').read_text()
        self.assertIn('hmac.compare_digest',source)
        self.assertIn("claims['request_hash']!=request_hash",source)
        self.assertIn("set(claims)!={'instance_id','company_id','operation_key','request_hash','approval_id','approved_by','expires_at'}",source)


class UncertaintyTests(BacklogBase):
    def test_21_timeout_before_commit_keeps_result_unknown(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'before-commit')
        self.provider.timeout_before=1
        response=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['status'],'reconciliation_required')
        self.assertEqual(self.provider.writes,0)
        reconciled=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':'before-commit'})
        self.assertEqual(reconciled.status_code,200,reconciled.text)
        self.assertEqual(reconciled.json()['status'],'reconciliation_required')
        state,ledger=self.ledger('before-commit')
        self.assertEqual(state,'reconciliation_required');self.assertTrue(ledger['reconciliation_required'])
        self.assertEqual(self.provider.writes,0)

    def test_22_lost_ack_after_commit_reconciles_one_effect(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'after-commit')
        self.provider.timeout_once=True
        first=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body)
        self.assertEqual(first.json()['status'],'reconciliation_required')
        self.assertEqual(self.provider.writes,1)
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).json()['status'],'reconciliation_required')
        final=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':'after-commit'})
        self.assertEqual(final.json()['status'],'succeeded',final.text)
        self.assertEqual(self.provider.writes,1);self.assertEqual(len(self.provider.operations),1)

    def test_23_concurrent_same_key_yields_one_remote_operation(self):
        proposal=self.partner_proposal();request=CommitRequest(**self.approved_body(proposal,'concurrent-write'))
        def run(_):return self.adapter.commit_write(self.actor,self.cid,request,'concurrent-write')
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,range(2)))
        self.assertEqual(self.provider.writes,1)
        self.assertTrue({r['status'] for r in results}<={'succeeded','reconciliation_required'},results)
        final=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':'concurrent-write'})
        self.assertEqual(final.json()['status'],'succeeded',final.text)
        replay=self.client.post(self.api+'/partners/commit',headers=self.owner,json=request.model_dump(mode='json'))
        self.assertEqual(replay.json()['remote_id'],final.json()['remote_id'])
        self.assertEqual(self.provider.writes,1)

    def test_24_same_key_with_other_content_is_a_stable_conflict(self):
        first=self.partner_proposal();second=self.partner_proposal()
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=self.approved_body(first,'shared-key')).json()['status'],'succeeded')
        response=self.client.post(self.api+'/partners/commit',headers=self.owner,json=self.approved_body(second,'shared-key'))
        self.assertEqual(response.status_code,409,response.text)
        self.assertEqual(response.json()['code'],'idempotency_conflict')
        self.assertEqual(self.provider.writes,1)

    def test_25_restart_between_remote_effect_and_local_record(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'restart-key')
        first=self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).json()
        self.assertEqual(first['status'],'succeeded')
        intent={'status':'reconciliation_required','local_id':proposal['id'],'remote_id':None,
                'operation_key':next(iter(self.provider.operations)),'proposal_id':proposal['id'],
                'proposal_hash':proposal['proposal_hash'],'approval_id':body['approval_id'],
                'payload_hash':digest(proposal['payload']),'reconciliation_required':True,'retryable':False}
        with self.app.state.db.transaction() as c:
            c.execute("UPDATE idempotency_keys SET state='pending',body=? WHERE company_id=? AND operation='write' AND key=?",(canonical(intent),self.cid,'restart-key'))
            c.execute('DELETE FROM external_links WHERE company_id=?',(self.cid,))
        recovered=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':'restart-key'})
        self.assertEqual(recovered.status_code,200,recovered.text)
        self.assertEqual(recovered.json()['status'],'succeeded')
        self.assertEqual(recovered.json()['remote_id'],first['remote_id'])
        self.assertEqual(self.provider.writes,1)

    def test_26_absent_ledger_and_permission_error_are_distinct(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal,'ledger-absent')
        self.provider.timeout_before=1
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).json()['status'],'reconciliation_required')
        absence=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':'ledger-absent'})
        self.assertEqual(absence.json()['status'],'reconciliation_required')
        self.provider.status_error=IntegrationError('provider_auth','Synthetic permission failure',424)
        denied=self.client.post(self.api+'/writes/reconcile',headers=self.owner,json={'idempotency_key':'ledger-absent'})
        self.assertGreaterEqual(denied.status_code,400)
        self.assertIn(denied.json()['code'],('provider_auth','not_ready','principal_revoked'))
        state,ledger=self.ledger('ledger-absent')
        self.assertEqual(state,'reconciliation_required');self.assertTrue(ledger['reconciliation_required'])
        self.assertEqual(self.provider.writes,0)


class PersistedRetentionTests(BacklogBase):
    def test_expired_key_reports_review_without_repeating_effect(self):
        proposal = self.partner_proposal()
        body = self.approved_body(proposal, 'retention-repeat')
        first = self.client.post(self.api+'/partners/commit', headers=self.owner, json=body)
        self.assertEqual(first.status_code, 200, first.text)
        with self.app.state.db.transaction() as connection:
            row = connection.execute(
                "SELECT body FROM idempotency_keys WHERE key=?", ('retention-repeat',)
            ).fetchone()
            stored = json.loads(row['body'])
            stored['created_at'] = (datetime.now(timezone.utc)-timedelta(days=50)).isoformat()
            connection.execute("UPDATE idempotency_keys SET body=? WHERE key=?",
                               (canonical(stored), 'retention-repeat'))
        repeated = self.client.post(self.api+'/partners/commit', headers=self.owner, json=body)
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertEqual(repeated.json()['retention_state'], 'expired_manual_review')
        self.assertEqual(repeated.json()['remote_id'], first.json()['remote_id'])
        self.assertEqual(self.provider.writes, 1)


class LedgerRetentionTests(unittest.TestCase):
    def test_27_key_lives_until_the_last_reconcilable_path(self):
        self.assertEqual(retention_days(),max(1,7,35)+7)
        self.assertEqual(retention_window(),timedelta(days=42))
        moment=datetime.now(timezone.utc)
        self.assertEqual(classify(moment-timedelta(days=41),moment),'reconcilable')
        self.assertEqual(classify(moment-timedelta(days=43),moment),'expired_manual_review')
        self.assertEqual(classify((moment-timedelta(days=10)).isoformat(),moment),'reconcilable')
        with self.assertRaises(ValueError):classify(moment+timedelta(hours=1),moment)


class PaginationTests(BacklogBase):
    def test_41_identical_write_dates_resume_without_loss(self):
        server=fixtures.PureTests().server()
        self.provider.partners=[{**self.provider.partners[0],'id':i,'name':'Same fixture name','write_date':'2026-11-09 10:00:00'} for i in range(1,251)]
        rows=[row for page in read_partners(self.provider,server) for row in page]
        self.assertEqual([int(r['external_id']) for r in rows],list(range(1,251)))
        self.assertEqual(len(rows),len({r['external_id'] for r in rows}))

    def test_45_ambiguous_identities_are_not_deduplicated(self):
        self.provider.partners=[{**self.provider.partners[0],'id':501,'vat':'ESB11111111'},
                                {**self.provider.partners[0],'id':502,'vat':'ESB11111111'}]
        preview=self.adapter.preview(self.bot,self.cid,'partners',True,'ambiguous')
        result=self.adapter.import_stages(self.bot,self.cid,preview['staging_ids'],'ambiguous-import','ambiguous')
        self.assertEqual(result['imported'],2)
        with self.app.state.db.connection() as c:partners=self.app.state.db.list(c,self.cid,'erp_partner')
        self.assertEqual(len(partners),2)
        self.assertEqual({p['remote_id'] for p in partners},{501,502})

    def test_51_partial_batch_reports_blocked_and_imported(self):
        self.provider.snapshot['move']['currency']='USD'
        blocked=self.adapter.preview(self.bot,self.cid,'invoices',True,'blocked-batch')['staging_ids']
        self.provider.snapshot['move']['currency']='EUR'
        valid=self.adapter.preview(self.bot,self.cid,'invoices',True,'valid-batch')['staging_ids']
        result=self.adapter.import_stages(self.bot,self.cid,blocked+valid,'mixed-batch','mixed')
        self.assertEqual(result['mapping_blocked'],1,result)
        self.assertEqual(result['imported'],1,result)


class SentinelTests(BacklogBase):
    def test_20_no_sentinel_secret_reaches_public_outputs(self):
        self.import_invoice('sentinel-import')
        texts=[]
        for path in ('/health','/capabilities','/metrics','/events','/staging','/conflicts','/audit-integrity','/briefing'):
            texts.append(self.client.get(self.api+path,headers=self.owner).text)
        for path in ('/tax-records','/export'):
            texts.append(self.client.get(self.root+path,headers=self.owner).text)
        texts.append(self.client.post(self.api+'/partners/commit',headers=self.agent,json={'proposal_id':'0'*32,'approval_id':'1'*32,'expected_revision':0,'idempotency_key':'sentinel-key'}).text)
        with self.app.state.db.connection() as c:texts.extend(r['body'] for r in c.execute('SELECT body FROM audit WHERE company_id=?',(self.cid,)))
        joined='\n'.join(texts)
        for secret in (self.settings['ODOO_BOT_KEY'],self.settings['ODOO_BRIDGE_SIGNING_KEY'],
                       self.settings['ODOO_DOCUMENT_KEY'],self.server['database'],'fixture-token'):
            self.assertNotIn(secret,joined)
        self.assertNotIn('sentinel',joined.lower())


class ContractTests(BacklogBase):
    def test_55_committed_schemas_match_the_models(self):
        root=Path(__file__).resolve().parents[1]
        committed=json.loads((root/'docs/odoo-adapter/schemas/contracts-v1.json').read_text())
        self.assertEqual(committed,export())
        self.assertEqual(committed['schema_version'],1)
        self.assertEqual(committed['mapping_version'],'odoo19-v1')
        for name in ('CapabilityReport','Conflict','ExternalObjectLink','ImportPreview','OperationEnvelope','OperationResult','SyncCursor','SyncJob'):
            self.assertIn(name,committed['models'])
            self.assertFalse(committed['models'][name]['additionalProperties'],name)

    def test_55_dtos_round_trip_the_consumed_examples(self):
        envelope=OperationEnvelope(tenant_id='standalone:'+'a'*32,company_id='a'*32,actor_id='bot',
                                   capability='partners.propose',correlation_id='correlation-fixture',
                                   idempotency_key='key-fixture',expected_revision=0,payload={'kind':'partner'})
        self.assertEqual(OperationEnvelope.model_validate_json(envelope.model_dump_json()),envelope)
        result=OperationResult(status='reconciliation_required',reconciliation_required=True)
        self.assertEqual(result.model_validate_json(result.model_dump_json()),result)
        with self.assertRaises(ValueError):OperationEnvelope(**{**envelope.model_dump(),'capability':'writes.commit','unknown':1})

    def test_56_every_emitted_error_code_has_a_contract(self):
        root=Path(__file__).resolve().parents[1]
        codes=set()
        for path in root.joinpath('agntia_gestoria').rglob('*.py'):
            codes.update(re.findall(r"(?:reject|IntegrationError)\('([a-z_]+)'",path.read_text(encoding='utf-8')))
        self.assertTrue(codes)
        self.assertEqual(sorted(codes-set(CONTRACT)),[])

    def test_56_public_error_is_sanitized_and_actionable(self):
        body=IntegrationError('timeout','Tiempo de espera Odoo agotado',504,True,True).public('correlation-fixture')
        self.assertEqual(set(body),{'code','message','correlation_id','retryable','reconciliation_required','category','next_action'})
        self.assertEqual(body['category'],'provider');self.assertEqual(body['next_action'],'reconcile_write')
        unknown=IntegrationError('some_future_code','Detalle interno',400).public()
        self.assertEqual(unknown['category'],'integration');self.assertEqual(unknown['next_action'],'report_with_correlation_id')

    def test_57_capabilities_expose_freshness_and_provenance(self):
        fresh=self.client.get(self.api+'/capabilities',headers=self.owner).json()
        self.assertFalse(fresh['stale']);self.assertTrue(fresh['checked_at']);self.assertTrue(fresh['expires_at'])
        self.assertFalse(fresh['remote_publication']);self.assertFalse(fresh['official_filing'])
        with self.app.state.db.transaction() as c:
            connection=self.adapter._connection(c,self.cid,json.loads(c.execute('SELECT body FROM provider_connections WHERE company_id=?',(self.cid,)).fetchone()['body'])['id'])
            connection['report']['expires_at']='2000-01-01T00:00:00+00:00';self.adapter.save_connection(c,connection)
        self.assertTrue(self.client.get(self.api+'/capabilities',headers=self.owner).json()['stale'])

    def test_64_metrics_are_labelled_per_capability_without_secrets(self):
        self.import_invoice('metrics-import')
        body=self.client.get(self.api+'/metrics',headers=self.owner).json()
        self.assertGreater(body['sample_size'],0);self.assertIsNotNone(body['latency_p50_ms'])
        self.assertTrue(body['by_operation'])
        for name,summary in body['by_operation'].items():
            self.assertEqual(set(summary),{'sample_size','latency_p50_ms','latency_p95_ms','failures'},name)
        self.assertIn('agntia.bridge.server_info',body['by_operation'])
        self.assertNotIn(self.settings['ODOO_BOT_KEY'],json.dumps(body))


if __name__=='__main__':unittest.main()
