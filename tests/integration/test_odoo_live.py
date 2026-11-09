"""Real Odoo suite. Explicit opt-in and private synthetic marker required.
These tests are NOT executed by the default unit suite or mocked as a live PASS.
"""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from agntia_gestoria.app import create_app
from agntia_gestoria.auth import Actor
from agntia_gestoria.integrations.odoo.adapter import Adapter
from agntia_gestoria.integrations.odoo.transport import Client
from agntia_gestoria.integrations.contracts import ConnectionCreate,BindingValidation,PartnerChange,ApprovalRequest,CommitRequest
from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.registry import load_server


@unittest.skipUnless(os.getenv('AGNTIA_RUN_ODOO_TESTS')=='1','Real Odoo opt-in required')
class LiveOdoo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=Path(os.environ['AGNTIA_LAB_STATE_DIR']).resolve()
        if not (cls.state/'AGNTIA_SYNTHETIC_LAB.json').is_file():raise RuntimeError('Synthetic lab marker missing')
        cls.settings=json.loads((cls.state/'run-env.json').read_text());cls.fixtures=json.loads((cls.state/'fixtures.private.json').read_text())
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        from agntia_gestoria.storage import Database
        local=Database(self.root)
        with sqlite3.connect(self.state/'gestoria-data/gestoria.sqlite3') as source,local.transaction() as destination:
            for row in source.execute('SELECT id,body FROM companies'):destination.execute('INSERT INTO companies VALUES(?,?)',row)
        self.env=patch.dict(os.environ,{**self.settings,'GESTORIA_DATA_DIR':str(self.root)});self.env.start()
        self.app=create_app(self.root);self.client=TestClient(self.app);self.adapter=Adapter(self.app.state.db);self.owner=Actor('owner','owner',('*',));self.headers={'Authorization':'Bearer '+self.fixtures['owner_token']}
        self.a,self.b=self.fixtures['companies'];self.cid=self.a['gestoria_company_id'];self.path='/api/companies/'+self.cid+'/integrations/odoo'
        for f in [self.a,self.b]:
            try:conn,_=self.adapter.scope(self.owner,f['gestoria_company_id'],'connections.manage',ready=False)
            except IntegrationError:
                self.adapter.create_connection(self.owner,f['gestoria_company_id'],ConnectionCreate(server_ref=f['server_ref']),'live-fixture');conn,_=self.adapter.scope(self.owner,f['gestoria_company_id'],'connections.manage',ready=False)
            self.adapter.validate(self.owner,f['gestoria_company_id'],BindingValidation(revision=conn['revision'],confirm_fiscal_identity=True,notes='Synthetic lab binding checked explicitly'),'live-fixture')
    def tearDown(self):self.client.close();self.env.stop();self.tmp.cleanup()
    def test_00_generic_write_guard_is_enforced(self):
        # No action_post is called, even in a negative test. Test a harmless fixture rename.
        client=Client(load_server(self.a['server_ref']))
        with self.assertRaises(IntegrationError):client._once('res.partner','write',{'ids':[self.a['partner_id']],'vals':{'name':'UNAUTHORIZED FIXTURE CHANGE'}})
        snapshots=client.call('agntia.bridge','invoice_snapshots',{'company_id':self.a['company_id'],'ids':[self.a['invoice_id']]})
        self.assertEqual(snapshots[0]['move']['state'],'draft')
    def test_A_import_evidence_review_calculation_report(self):
        preview=self.adapter.preview(self.owner,self.cid,'invoices',True,'live-A');result=self.adapter.import_stages(self.owner,self.cid,preview['staging_ids'],'live-A-'+uuid.uuid4().hex,'live-A')
        records=self.client.get('/api/companies/'+self.cid+'/tax-records',headers=self.headers).json()
        records=[r for r in records if r.get('provenance',{}).get('remote_invoice_id')==self.a['invoice_id'] and r['status']!='void']
        self.assertTrue(records);record=records[0];self.assertEqual(record['status'],'unverified')
        doc=self.adapter.download_attachment(self.owner,self.cid,self.a['invoice_id'],self.a['attachment_id'],'live-A')
        body={'revision':record['revision'],'operation_date':'2026-04-10','tax_kind':'iva','category':'ordinary','vat_treatment':'domestic_current','tax_rate':'21','deductible_tax_amount':None,'deductible_irpf_amount':None,'document_ids':[doc['id']],'notes':'Synthetic path only; not proof of a real issued fiscal invoice','issued_evidence_confirmed':True}
        r=self.client.post(self.path+'/records/'+record['id']+'/classification',headers=self.headers,json=body);self.assertEqual(r.status_code,200,r.text)
        r=self.client.post('/api/companies/'+self.cid+'/tax-records/'+record['id']+'/review',headers=self.headers,json={'revision':r.json()['revision'],'notes':'Synthetic human evidence review'});self.assertEqual(r.status_code,200,r.text)
        result=self.client.post('/api/companies/'+self.cid+'/tax-calculations',headers=self.headers,json={'model':'303','year':2026,'period':'2T','regime':'iva_general_domestic','confirmed_standard_scope':True})
        self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()['boxes']['71'],'21.00')
        self.assertEqual(self.client.post('/api/companies/'+self.cid+'/reports',headers=self.headers,json={'year':2026}).status_code,200)
    def test_B_canary_import_never_activates_common_engine(self):
        cid=self.b['gestoria_company_id'];preview=self.adapter.preview(self.owner,cid,'invoices',True,'live-B');self.adapter.import_stages(self.owner,cid,preview['staging_ids'],'live-B-'+uuid.uuid4().hex,'live-B')
        records=self.client.get('/api/companies/'+cid+'/tax-records',headers=self.headers).json();self.assertTrue(any(r['tax_kind']=='igic' for r in records))
        response=self.client.post('/api/companies/'+cid+'/tax-calculations',headers=self.headers,json={'model':'303','year':2026,'period':'2T','regime':'iva_general_domestic','confirmed_standard_scope':True})
        self.assertEqual(response.status_code,400)
    def test_C_two_databases_scopes_and_swapped_credentials(self):
        token=self.a['agent_token'];path='/api/companies/'+self.b['gestoria_company_id']+'/integrations/odoo/health'
        self.assertEqual(self.client.get(path,headers={'Authorization':'Bearer '+token}).status_code,404)
        server=load_server(self.a['server_ref']);server.database=self.b['database']
        with self.assertRaises(IntegrationError):Client(server).call('agntia.bridge','server_info',{'company_id':self.a['company_id']})
    def test_D_remote_change_after_review_creates_conflict_and_stale(self):
        preview=self.adapter.preview(self.owner,self.cid,'invoices',True,'live-D')
        imported=self.adapter.import_stages(self.owner,self.cid,preview['staging_ids'],'live-D-'+uuid.uuid4().hex,'live-D')
        record_id=imported['local_ids'][0]
        # Review and calculate using the dedicated synthetic test A path is tested independently.
        # This snapshot demonstrates invalidation on a real source mutation and preserves the original.
        from agntia_gestoria.storage import digest,canonical
        with self.app.state.db.transaction() as c:
            company=self.app.state.db.company(c,self.cid);records=sorted(self.app.state.db.list(c,self.cid,'tax_record'),key=lambda r:r['id'])
            calculation={'id':uuid.uuid4().hex,'company_id':self.cid,'data_fingerprint':digest({'company':company,'records':records})}
            self.app.state.db.put(c,self.cid,'tax_calculation',calculation)
        from scripts.odoo_bootstrap import compose
        change="m=env['account.move'].browse(%d); assert env.cr.dbname=='agntia_test_a' and m.state=='draft'; m.invoice_line_ids.filtered(lambda l:l.display_type=='product').write({'price_unit':200}); env.cr.commit()"%self.a['invoice_id']
        restore=change.replace("'price_unit':200","'price_unit':100")
        try:
            compose(self.state,'exec','-T','odoo','odoo','shell','-d','agntia_test_a','--no-http','--shell-interface','python',input=change,capture=True)
            self.adapter.preview(self.owner,self.cid,'invoices',True,'live-D-change')
            conflicts=self.client.get(self.path+'/conflicts',headers=self.headers).json();self.assertTrue(conflicts)
            calculations=self.client.get('/api/companies/'+self.cid+'/tax-calculations',headers=self.headers).json()
            self.assertTrue(calculations[0]['data_changed_since_calculation'])
            with self.app.state.db.connection() as c:self.assertEqual(self.app.state.db.get(c,self.cid,record_id,'tax_record')['base_amount'],'100.00')
        finally:compose(self.state,'exec','-T','odoo','odoo','shell','-d','agntia_test_a','--no-http','--shell-interface','python',input=restore,capture=True)

    def test_E_real_draft_replay_has_one_remote_operation(self):
        from agntia_gestoria.integrations.contracts import DraftInvoiceRequest
        response=self.client.post('/api/companies/'+self.cid+'/invoice-drafts',headers=self.headers,json={'customer_name':'Synthetic customer','operation_date':'2026-04-10','tax_kind':'iva','withholding_rate':'0','lines':[{'description':'Synthetic service','quantity':'1','unit_price':'100','tax_rate':'21'}]})
        self.assertEqual(response.status_code,200,response.text);draft=response.json()
        source=self.adapter.projection_input(self.owner,self.cid,draft['id'])
        p=self.adapter.propose_invoice(self.owner,self.cid,DraftInvoiceRequest(invoice_draft_id=draft['id'],partner_id=self.a['partner_id'],journal_id=self.a['journal_id'],account_id=self.a['account_id'],tax_ids=[self.a['tax_id']],expected_draft_hash=source['source_hash']),'live-E')
        approval=self.adapter.approve(self.owner,self.cid,p['id'],ApprovalRequest(revision=0,proposal_hash=p['proposal_hash'],notes='Synthetic draft creation approved'),'live-E')
        body=CommitRequest(proposal_id=p['id'],approval_id=approval['id'],expected_revision=0,idempotency_key='live-E-'+uuid.uuid4().hex)
        first=self.adapter.commit_write(self.owner,self.cid,body,'live-E');again=self.adapter.commit_write(self.owner,self.cid,body,'live-E')
        self.assertEqual(first['status'],'succeeded');self.assertEqual(first['remote_id'],again['remote_id']);self.assertEqual(first['remote_state'],'draft')
        # Simulate local ACK loss after the real Odoo transaction; reconciliation must not create again.
        from agntia_gestoria.storage import canonical
        with self.app.state.db.transaction() as c:
            uncertain={**first,'status':'reconciliation_required','remote_id':None,'reconciliation_required':True}
            c.execute("UPDATE idempotency_keys SET state='reconciliation_required',body=? WHERE company_id=? AND operation='write' AND key=?",(canonical(uncertain),self.cid,body.idempotency_key))
        reconciled=self.adapter.reconcile_write(self.owner,self.cid,body.idempotency_key,'live-E-recovery')
        self.assertEqual(reconciled['remote_id'],first['remote_id']);self.assertEqual(reconciled['status'],'succeeded')
        self.assertTrue(self.adapter.audit_integrity(self.owner,self.cid)['valid'])

if __name__=='__main__':unittest.main(failfast=True)
