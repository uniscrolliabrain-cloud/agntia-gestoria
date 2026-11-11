import json
import os
import tempfile
import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from agntia_gestoria.app import create_app, calendar_export
from agntia_gestoria.models import InvoiceDraft, JournalDraft, invoice_totals
from agntia_gestoria.rules import add_months, evaluate


class Finance(unittest.TestCase):
    def test_rounding_and_explicit_rates(self):
        d=InvoiceDraft(customer_name='Cliente',operation_date='2026-11-09',tax_kind='iva',withholding_rate='15',lines=[dict(description='Servicio',quantity='3',unit_price='0.335',tax_rate='21')])
        t=invoice_totals(d)
        self.assertEqual((t['base'],t['tax'],t['withholding'],t['total']),('1.01','0.21','0.15','1.07'))
        with self.assertRaises(ValueError):
            JournalDraft(entry_date='2026-11-09',concept='Asiento',lines=[dict(account='1',debit='1',credit='0'),dict(account='2',debit='0',credit='2')])

    def test_calendar(self):
        self.assertEqual(add_months(date(2024,1,31),1),date(2024,2,29))
        text=calendar_export([dict(id='test',due_date='2026-12-01',status='draft',title='Hola\nEND:VEVENT',description='á'*100)])
        self.assertIn('Hola\\nEND:VEVENT',text)
        self.assertTrue(all(len(line.encode())<=75 for line in text.split('\r\n')))

    def test_distinct_sif_b2b_and_real_approval_date(self):
        c=dict(id='a'*32,revision=0,legal_form='sl',tax_territory='common',facts={'fiscal_year_end':'2025-12-31','accounts_approved_on':'2026-05-15','corporate_taxpayer':True,'sif_in_scope':True,'b2b_einvoice_in_scope':True,'previous_year_turnover_over_8m':False})
        rules={x['rule_id']:x for x in evaluate(c,today=date(2026,11,9))['obligations']}
        self.assertEqual(rules['annual-deposit']['due_date'],'2026-06-15')
        self.assertEqual(rules['sif-adaptation']['due_date'],'2027-01-01')
        self.assertEqual(rules['b2b-invoices']['due_date'],'2028-10-06')
        c['legal_form']='autonomo'
        rules={x['rule_id']:x for x in evaluate(c,today=date(2026,11,9))['obligations']}
        self.assertEqual(rules['b2b-events']['due_date'],'2029-10-06')
        self.assertTrue(evaluate(c,today=date(2027,1,1))['pack_stale'])

    def test_all_territories_and_mixed_profile(self):
        from agntia_gestoria.models import CompanyCreate
        from agntia_gestoria.territories import TERRITORIES
        from agntia_gestoria.rules import catalogue
        known={x['id'] for x in catalogue()['sources']}
        for territory in TERRITORIES:
            c=CompanyCreate(name='Empresa nacional',legal_form='sl',tax_territory=territory,operation_territories=[territory]).model_dump(mode='json')
            c.update(id='a'*32,revision=0)
            result=evaluate(c,today=date(2026,11,9))
            self.assertEqual(result['territorial_profile']['declared_operation_territories'],[territory])
            for obligation in result['obligations']:
                self.assertFalse(set(obligation['source_ids'])-known)
            if territory!='common':
                self.assertTrue(any(o['rule_id']=='territory-'+territory for o in result['obligations']))
        c.update(tax_territory='common',operation_territories=['common','navarra'],tax_administrations={'iva':['aeat','navarra']})
        result=evaluate(c,today=date(2026,11,9))
        rules={o['rule_id']:o for o in result['obligations']}
        self.assertTrue(result['territorial_profile']['multiple_territories'])
        self.assertEqual(rules['vat-return']['applicability'],'outside_coverage')
        self.assertEqual(rules['multi-administration']['applicability'],'needs_facts')
        c.update(operation_territories=['common'],tax_administrations={'iva':['navarra']})
        self.assertEqual(next(o for o in evaluate(c)['obligations'] if o['rule_id']=='vat-return')['applicability'],'outside_coverage')
        with self.assertRaises(ValueError):
            CompanyCreate(name='Empresa',legal_form='sl',operation_territories=['invalid'])

    def test_unknown_vat_and_territory(self):
        c=dict(id='a'*32,revision=0,legal_form='autonomo',tax_territory='common',facts={'vat_status':'exempt'})
        r=evaluate(c,today=date(2026,11,9))
        vat=next(x for x in r['obligations'] if x['rule_id']=='vat-return')
        self.assertEqual(vat['applicability'],'needs_facts')
        c['tax_territory']='canarias'
        r=evaluate(c,today=date(2026,11,9))
        self.assertEqual(next(x for x in r['obligations'] if x['rule_id']=='vat-return')['applicability'],'outside_coverage')


class Service(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.env=patch.dict(os.environ,{'GESTORIA_OWNER_TOKEN':'owner-secret-token-12345','GESTORIA_ACTORS_JSON':json.dumps({'agent-secret-token-12345':{'id':'bot','role':'agent','companies':['*']}})})
        self.env.start()
        self.client=TestClient(create_app(self.tmp.name))
        self.owner={'Authorization':'Bearer owner-secret-token-12345'}
        self.agent={'Authorization':'Bearer agent-secret-token-12345'}
        r=self.client.post('/api/companies',headers=self.owner,json={'name':'Empresa SL','legal_form':'sl','tax_territory':'common'})
        self.assertEqual(r.status_code,200,r.text)
        self.company=r.json();self.root='/api/companies/'+self.company['id']

    def tearDown(self):
        self.client.close();self.env.stop();self.tmp.cleanup()

    def test_auth_and_role(self):
        self.assertEqual(self.client.get('/api/companies').status_code,401)
        self.assertEqual(self.client.post('/api/companies',headers=self.agent,json={'name':'Otra','legal_form':'sl'}).status_code,403)
        scoped={'scoped-secret-token-12345':{'id':'scoped','role':'viewer','companies':[]}}
        with patch.dict(os.environ,{'GESTORIA_ACTORS_JSON':json.dumps(scoped)}):
            self.assertEqual(self.client.get(self.root,headers={'Authorization':'Bearer scoped-secret-token-12345'}).status_code,404)

    def test_revision_and_review(self):
        r=self.client.post(self.root+'/cases',headers=self.agent,json={'title':'Tarea','source_ids':['lsc']})
        self.assertEqual(r.status_code,200,r.text)
        case=r.json();p=self.root+'/cases/'+case['id']
        self.assertEqual(self.client.post(p+'/close',headers=self.owner,json={'revision':0}).status_code,409)
        self.assertEqual(self.client.post(p+'/submit-review',headers=self.agent,json={'revision':0}).status_code,200)
        review={'revision':1,'decision':'approve','notes':'Fuente contrastada','verified_source_ids':['lsc']}
        self.assertEqual(self.client.post(p+'/review',headers=self.agent,json=review).status_code,403)
        self.assertEqual(self.client.post(p+'/review',headers=self.owner,json=review).status_code,200)
        edited=self.client.put(p,headers=self.agent,json={'revision':2,'title':'Nueva tarea','source_ids':['lsc']})
        self.assertEqual(edited.status_code,200,edited.text)
        self.assertIsNone(edited.json()['review'])
        self.assertEqual(self.client.post(p+'/close',headers=self.owner,json={'revision':3}).status_code,409)
        self.assertEqual(self.client.put(p,headers=self.agent,json={'revision':2,'title':'Obsoleto'}).status_code,409)

    def test_reviewed_close_and_cross_company_document(self):
        document=self.client.post(self.root+'/documents',headers=self.owner,files={'file':('proof.txt',b'Proof')}).json()
        other=self.client.post('/api/companies',headers=self.owner,json={'name':'Otra empresa','legal_form':'autonomo'}).json()
        path='/api/companies/'+other['id']+'/cases'
        self.assertEqual(self.client.post(path,headers=self.owner,json={'title':'Otra tarea','document_ids':[document['id']]}).status_code,404)
        case=self.client.post(self.root+'/cases',headers=self.agent,json={'title':'Tarea sin fuentes'}).json()
        path=self.root+'/cases/'+case['id']
        self.client.post(path+'/submit-review',headers=self.agent,json={'revision':0})
        self.assertEqual(self.client.post(path+'/review',headers=self.owner,json={'revision':1,'decision':'approve','notes':'Revisión interna completada','verified_source_ids':[]}).status_code,200)
        self.assertEqual(self.client.post(path+'/close',headers=self.agent,json={'revision':2}).status_code,403)
        closed=self.client.post(path+'/close',headers=self.owner,json={'revision':2})
        self.assertEqual(closed.status_code,200,closed.text)
        self.assertEqual(closed.json()['outcome'],'internal_complete')

    def test_national_profile_api_round_trip(self):
        body={'name':'Nacional SL','legal_form':'sl','tax_territory':'common','operation_territories':['common','canarias','bizkaia','navarra','ceuta','melilla'],'tax_administrations':{'iva':['aeat','bizkaia'],'igic':['atc'],'ipsi':['ceuta','melilla']}}
        response=self.client.post('/api/companies',headers=self.owner,json=body)
        self.assertEqual(response.status_code,200,response.text)
        company=response.json();root='/api/companies/'+company['id']
        self.assertEqual(company['operation_territories'],body['operation_territories'])
        plan=self.client.get(root+'/obligations',headers=self.agent).json()
        self.assertEqual(plan['territorial_profile']['tax_administrations']['iva'],['aeat','bizkaia'])
        result=self.client.post(root+'/generate-plan',headers=self.agent,json={'revision':0})
        self.assertEqual(result.status_code,200,result.text)
        titles=[c['title'] for c in self.client.get(root+'/cases',headers=self.owner).json()]
        self.assertTrue(any('Ceuta' in title for title in titles))
        self.assertTrue(any('Canarias' in title for title in titles))

    def test_tax_record_duplicate_period_summary_and_changes(self):
        record={'external_id':'invoice-1','operation_date':'2026-03-31','kind':'income','description':'Venta','tax_kind':'iva','base_amount':'100.10','tax_amount':'21.02','withholding_amount':'15.02'}
        created=self.client.post(self.root+'/tax-records',headers=self.agent,json=record)
        self.assertEqual(created.status_code,200,created.text)
        record_id=created.json()['id']
        self.assertEqual(self.client.post(self.root+'/tax-records',headers=self.agent,json=record).status_code,409)
        record.update(external_id='invoice-2',operation_date='2026-04-01',base_amount='200')
        self.client.post(self.root+'/tax-records',headers=self.agent,json=record)
        prepared=self.client.post(self.root+'/tax-preparations',headers=self.agent,json={'model':'303','year':2026,'period':'1T','administration':'aeat'})
        self.assertEqual(prepared.status_code,200,prepared.text)
        result=prepared.json()
        self.assertEqual(result['record_ids'],[record_id])
        self.assertEqual(result['arithmetic_summary']['income:iva']['base_amount'],'100.10')
        self.assertIsNone(result['official_tax_result']);self.assertFalse(result['filing_ready'])
        self.assertFalse(self.client.get(self.root+'/tax-preparations',headers=self.owner).json()[0]['data_changed_since_preparation'])
        self.assertEqual(self.client.post(self.root+'/tax-records/'+record_id+'/void',headers=self.agent,json={'revision':0}).status_code,200)
        self.assertEqual(self.client.post(self.root+'/tax-records/'+record_id+'/void',headers=self.agent,json={'revision':0}).status_code,409)
        self.assertTrue(self.client.get(self.root+'/tax-preparations',headers=self.owner).json()[0]['data_changed_since_preparation'])
        again=self.client.post(self.root+'/tax-preparations',headers=self.agent,json={'model':'303','year':2026,'period':'1T','administration':'aeat'}).json()
        self.assertEqual(again['record_ids'],[])
        export=self.client.get(self.root+'/export',headers=self.owner).json()
        self.assertEqual(len(export['tax_records']),2)
        self.assertEqual(len(export['tax_preparations']),2)

    def test_tax_records_scoped_and_preparation_validation(self):
        doc=self.client.post(self.root+'/documents',headers=self.owner,files={'file':('receipt.txt',b'Original')}).json()
        other=self.client.post('/api/companies',headers=self.owner,json={'name':'Autonomo','legal_form':'autonomo'}).json()
        root='/api/companies/'+other['id']
        record={'external_id':'ref','operation_date':'2026-01-01','kind':'expense','description':'Gasto','tax_kind':'none','base_amount':'20','tax_amount':'0','document_ids':[doc['id']]}
        self.assertEqual(self.client.post(root+'/tax-records',headers=self.agent,json=record).status_code,404)
        record['document_ids']=[];record['tax_amount']='1'
        self.assertEqual(self.client.post(root+'/tax-records',headers=self.agent,json=record).status_code,422)
        body={'model':'100','year':2026,'period':'annual','administration':'aeat'}
        self.assertEqual(self.client.post(self.root+'/tax-preparations',headers=self.agent,json=body).status_code,400)
        personal=self.client.post(root+'/tax-preparations',headers=self.agent,json=body)
        self.assertEqual(personal.status_code,200,personal.text)
        self.assertTrue(any('personales' in b for b in personal.json()['blockers']))
        body.update(model='130',period='annual')
        self.assertEqual(self.client.post(root+'/tax-preparations',headers=self.agent,json=body).status_code,422)
        body.update(model='390',period='1T')
        self.assertEqual(self.client.post(root+'/tax-preparations',headers=self.agent,json=body).status_code,422)
        scoped={'viewer-secret-token-12345':{'id':'viewer','role':'viewer','companies':[other['id']]}}
        with patch.dict(os.environ,{'GESTORIA_ACTORS_JSON':json.dumps(scoped)}):
            headers={'Authorization':'Bearer viewer-secret-token-12345'}
            self.assertEqual(self.client.get(self.root+'/tax-records',headers=headers).status_code,404)
            self.assertEqual(self.client.post(root+'/tax-preparations',headers=headers,json={'model':'100','year':2026,'period':'annual','administration':'aeat'}).status_code,403)

    def test_plan_idempotent_upload_and_static(self):
        a=self.client.post(self.root+'/generate-plan',headers=self.agent,json={'revision':0})
        self.assertEqual(a.status_code,200,a.text)
        b=self.client.post(self.root+'/generate-plan',headers=self.agent,json={'revision':0}).json()
        self.assertGreater(len(a.json()['created']),0);self.assertEqual(b['created'],[])
        self.assertEqual(self.client.post(self.root+'/documents',headers=self.agent,files={'file':('bad.pdf',b'wrong')}).status_code,400)
        d=self.client.post(self.root+'/documents',headers=self.agent,files={'file':('../../notes.txt',b'Hola')})
        self.assertEqual(d.status_code,200,d.text);self.assertEqual(d.json()['name'],'notes.txt')
        self.assertEqual(self.client.get('/',headers=self.owner).status_code,200)
        self.assertGreater(len(self.client.get(self.root+'/audit',headers=self.owner).json()),0)

if __name__=='__main__':unittest.main()
