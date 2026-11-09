import io
import json
import os
import tempfile
import unittest
import zipfile
from copy import deepcopy
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient
from agntia_gestoria.app import create_app
from agntia_gestoria.analytics import analyze,infographic,presentation,report_html,report_pdf
from agntia_gestoria.engines import Calculation,calculate


def company():
    return {'id':'a'*32,'name':'Empresa <ejemplo>','revision':0,'legal_form':'autonomo','tax_territory':'common','operation_territories':['common'],'tax_administrations':{},'facts':{'irpf_payment_model':'130','vat_status':'liable','vat_return_required':True,'vat_periodicity':'quarterly'}}


def record(key,kind,base,tax,day='2026-04-01',retention='0',deductible=None):
    return {'id':str(key).zfill(32),'external_id':str(key),'revision':1,'status':'reviewed','operation_date':day,'kind':kind,'description':'Operación','counterparty':'Cliente A' if kind=='income' else 'Proveedor','category':'ordinary','vat_treatment':'domestic_current','base_amount':base,'tax_amount':tax,'tax_kind':'iva','tax_rate':'21','withholding_amount':retention,'deductible_tax_amount':tax if kind=='expense' else None,'deductible_irpf_amount':deductible or base if kind=='expense' else None,'document_ids':['f'*32]}


def request(model='303',**kwargs):
    return Calculation(model=model,year=2026,period=kwargs.pop('period','2T'),regime='iva_general_domestic' if model=='303' else 'irpf_direct_normal',confirmed_standard_scope=True,**kwargs)


class Engines(unittest.TestCase):
    def test_vat_credit_consumption_and_negative_period(self):
        rows=[record(1,'income','1000','210'),record(2,'expense','200','42')]
        r=calculate(company(),rows,request(prior_vat_credit='200'))
        self.assertEqual((r['boxes']['27'],r['boxes']['45'],r['boxes']['71'],r['boxes']['87']),('210.00','42.00','0.00','32.00'))
        self.assertEqual(r['boxes']['78'],'168.00')
        negative=calculate(company(),rows[1:],request(prior_vat_credit='200'))
        self.assertEqual(negative['boxes']['78'],'0.00');self.assertEqual(negative['boxes']['87'],'200.00')
        self.assertEqual(negative['result']['credit_generated_this_period'],'42.00')
        no_apply=calculate(company(),rows,request(prior_vat_credit='200',apply_prior_vat_credit=False))
        self.assertEqual(no_apply['boxes']['71'],'168.00')

    def test_non_vat_expense_is_explicitly_excluded_from_boxes(self):
        rows=[record(1,'income','1000','210'),record(2,'expense','300','0')]
        rows[1].update(tax_kind='none',tax_rate=None,vat_treatment='exempt',deductible_tax_amount='0')
        result=calculate(company(),rows,request())
        self.assertEqual(result['boxes']['71'],'210.00')
        self.assertEqual(result['boxes']['28'],'0.00')
        self.assertEqual(result['excluded_from_boxes'][0]['id'],rows[1]['id'])

    def test_vat_rate_groups_and_quarter_boundary(self):
        rows=[record(1,'income','1000','210'),record(2,'income','100','10'),record(3,'income','100','4'),record(4,'income','50','10.50',day='2026-07-01')]
        rows[1]['tax_rate']='10';rows[2]['tax_rate']='4'
        r=calculate(company(),rows,request())
        self.assertEqual(r['boxes']['27'],'224.00');self.assertEqual(r['boxes']['03'],'4.00');self.assertEqual(len(r['record_ids']),3)
        rows[0]['operation_date']='2026-03-31'
        first=calculate(company(),rows,request(period='1T'))
        self.assertTrue(first['source_url'].endswith('instrucciones-2026.html'))

    def test_irpf_ytd_previous_payments_and_minoracion(self):
        rows=[record(1,'income','10000','2100',day='2026-01-20',retention='500'),record(2,'income','8000','1680'),record(3,'expense','2000','420',day='2026-02-20'),record(4,'expense','3000','630')]
        r=calculate(company(),rows,request('130',previous_year_net_activity_income='11000',prior_130_positive_box07_sum='1600',prior_130_unused_negative='100'))
        self.assertEqual(r['boxes']['01'],'18000.00');self.assertEqual(r['boxes']['02'],'5000.00')
        self.assertEqual(r['boxes']['04'],'2600.00');self.assertEqual(r['boxes']['07'],'500.00')
        self.assertEqual(r['boxes']['13'],'50.00');self.assertEqual(r['boxes']['19'],'350.00')
        self.assertEqual(r['period_start'],'2026-01-01')

    def test_irpf_minoracion_boundaries_and_negative_signs(self):
        rows=[record(1,'expense','100','21')]
        for income,reduction in [('9000','100.00'),('9000.01','75.00'),('10000','75.00'),('10000.01','50.00'),('11000.01','25.00'),('12000.01','0.00')]:
            r=calculate(company(),rows,request('130',previous_year_net_activity_income=income))
            self.assertEqual(r['boxes']['13'],reduction)
            self.assertEqual(Decimal(r['boxes']['19']),-Decimal(reduction))
        with self.assertRaises(ValueError):request('130',period='1T',previous_year_net_activity_income='0',prior_130_positive_box07_sum='10')

    def test_explicit_rejections_no_silent_omissions(self):
        rows=[record(1,'income','1000','210')]
        for change in [{'status':'unverified'},{'vat_treatment':'intra_eu'},{'document_ids':[]},{'category':'asset'},{'tax_amount':'209.99'},{'kind':'adjustment'}]:
            invalid=deepcopy(rows);invalid[0].update(change)
            with self.assertRaises(ValueError,msg=str(change)):calculate(company(),invalid,request())
        c=company();c['operation_territories']=['common','navarra']
        with self.assertRaises(ValueError):calculate(c,rows,request())
        c=company();c['facts']['vat_return_required']=None
        with self.assertRaises(ValueError):calculate(c,rows,request())
        with self.assertRaises(ValueError):Calculation(model='303',year=2025,period='2T',regime='iva_general_domestic',confirmed_standard_scope=True)
        expense=record(2,'expense','100','21');expense['deductible_tax_amount']='10'
        with self.assertRaises(ValueError):calculate(company(),[expense],request())


class Reports(unittest.TestCase):
    def test_metrics_alerts_and_exports(self):
        rows=[record(1,'income','1000','210'),record(2,'expense','200','42'),record(3,'expense','200','42')]
        rows[2].update(status='unverified',document_ids=[])
        report=analyze(company(),rows,[],[],2026)
        self.assertEqual(report['metrics']['operating_difference'],'600.00')
        self.assertEqual(report['metrics']['reviewed_count'],2)
        self.assertTrue({'possible_duplicate','missing_documents','unreviewed','concentration'}<=set(a['code'] for a in report['alerts']))
        svg=infographic(report);self.assertIn('Empresa &lt;ejemplo&gt;',svg)
        self.assertNotIn('<ejemplo>',report_html(report))
        self.assertTrue(report_pdf(report).startswith(b'%PDF-'))
        pptx=presentation(report)
        from pptx import Presentation
        deck=Presentation(io.BytesIO(pptx));self.assertGreaterEqual(len(deck.slides),6)
        self.assertTrue(any(shape.has_chart for slide in deck.slides for shape in slide.shapes))
        fingerprint=report['report_fingerprint']
        self.assertEqual(fingerprint,analyze(company(),rows,[],[],2026)['report_fingerprint'])
        self.assertNotEqual(fingerprint,analyze(company(),rows,[],[{'id':'b'*32,'status':'draft'}],2026)['report_fingerprint'])

    def test_negative_adjustments_chart_has_valid_geometry(self):
        rows=[record(1,'income','-50','-10.50')]
        report=analyze(company(),rows,[],[],2026)
        self.assertEqual(report['metrics']['income_base'],'-50.00')
        import xml.etree.ElementTree as ET
        root=ET.fromstring(infographic(report))
        for rect in root.findall('{http://www.w3.org/2000/svg}rect'):
            self.assertGreaterEqual(float(rect.attrib.get('height','0')),0)


class API(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.env=patch.dict(os.environ,{'GESTORIA_OWNER_TOKEN':'owner-token-test-123456','GESTORIA_ACTORS_JSON':json.dumps({'agent-token-test-123456':{'id':'bot','role':'agent','companies':['*']}})});self.env.start()
        self.client=TestClient(create_app(self.tmp.name));self.owner={'Authorization':'Bearer owner-token-test-123456'};self.agent={'Authorization':'Bearer agent-token-test-123456'}
        c=company();payload={k:v for k,v in c.items() if k not in ('id','revision')}
        response=self.client.post('/api/companies',headers=self.owner,json=payload);self.assertEqual(response.status_code,200,response.text)
        self.root='/api/companies/'+response.json()['id']
        self.document=self.client.post(self.root+'/documents',headers=self.owner,files={'file':('invoice.txt',b'Example original')}).json()['id']
    def tearDown(self):self.client.close();self.env.stop();self.tmp.cleanup()
    def create(self):
        row=record(1,'income','1000','210');row={k:v for k,v in row.items() if k not in ('id','status','revision')};row['document_ids']=[self.document]
        response=self.client.post(self.root+'/tax-records',headers=self.agent,json=row);self.assertEqual(response.status_code,200,response.text);return response.json()
    def test_calculation_review_and_saved_report(self):
        row=self.create();path=self.root+'/tax-records/'+row['id']+'/review'
        body=request().model_dump(mode='json')
        self.assertEqual(self.client.post(self.root+'/tax-calculations',headers=self.agent,json=body).status_code,400)
        self.assertEqual(self.client.post(path,headers=self.agent,json={'revision':0,'notes':'Reviewed'}).status_code,403)
        self.assertEqual(self.client.post(path,headers=self.owner,json={'revision':0,'notes':'Original and classification checked'}).status_code,200)
        calculated=self.client.post(self.root+'/tax-calculations',headers=self.agent,json=body)
        self.assertEqual(calculated.status_code,200,calculated.text);self.assertEqual(calculated.json()['boxes']['71'],'210.00')
        report=self.client.post(self.root+'/reports',headers=self.agent,json={'year':2026})
        self.assertEqual(report.status_code,200,report.text)
        report=report.json()
        for suffix,magic in [('svg',b'<svg'),('pdf',b'%PDF'),('pptx',b'PK'),('html',b'<!doctype html>')]:
            download=self.client.get(self.root+'/reports/'+report['id']+'/download/'+suffix,headers=self.owner)
            self.assertEqual(download.status_code,200,download.text[:100] if suffix=='html' else suffix);self.assertTrue(download.content.startswith(magic))
        dashboard=self.client.get(self.root+'/dashboard?year=2026',headers=self.owner)
        self.assertEqual(dashboard.status_code,200);self.assertEqual(dashboard.json()['metrics']['income_base'],'1000.00')
        self.assertEqual(len(dashboard.json()['tax_calculations']),1)
        self.client.post(self.root+'/tax-records/'+row['id']+'/void',headers=self.agent,json={'revision':1})
        self.assertTrue(self.client.get(self.root+'/tax-calculations',headers=self.owner).json()[0]['data_changed_since_calculation'])
        self.assertTrue(self.client.get(self.root+'/reports',headers=self.owner).json()[0]['data_changed_since_report'])
    def test_import_is_atomic_and_preview_does_not_save(self):
        row=record(1,'income','1000','210');row={k:v for k,v in row.items() if k not in ('id','status','revision')};row['document_ids']=[self.document]
        response=self.client.post(self.root+'/tax-records/import',headers=self.agent,json={'records':[row,row]})
        self.assertEqual(response.status_code,409);self.assertEqual(self.client.get(self.root+'/tax-records',headers=self.owner).json(),[])
        csv=b'external_id,operation_date,kind,description,tax_kind,base_amount,tax_amount\ncsv-1,2026-04-01,income,Sale,iva,100,21\n'
        preview=self.client.post(self.root+'/tax-records/preview-csv',headers=self.agent,files={'file':('import.csv',csv)})
        self.assertEqual(preview.status_code,200,preview.text);self.assertTrue(preview.json()['can_import'])
        self.assertEqual(self.client.get(self.root+'/tax-records',headers=self.owner).json(),[])
        self.assertEqual(self.client.post(self.root+'/tax-records/import',headers=self.agent,json={'records':preview.json()['records']}).status_code,200)
    def test_company_scope_on_reports_and_dashboard(self):
        rpt=self.client.post(self.root+'/reports',headers=self.owner,json={'year':2026}).json()
        with patch.dict(os.environ,{'GESTORIA_ACTORS_JSON':json.dumps({'scoped-token-test-123456':{'id':'outsider','role':'viewer','companies':[]}})}):
            headers={'Authorization':'Bearer scoped-token-test-123456'}
            for path in ['/dashboard?year=2026','/reports','/reports/'+rpt['id']+'/download/svg','/tax-calculations']:
                self.assertEqual(self.client.get(self.root+path,headers=headers).status_code,404)

if __name__=='__main__':unittest.main()
