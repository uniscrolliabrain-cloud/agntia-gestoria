import hashlib
import hmac
import importlib.util
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import unittest
from unittest.mock import patch

from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.registry import Server,credentials,load_server
from agntia_gestoria.storage import canonical
import test_odoo_adapter as fixtures


class HardeningTests(unittest.TestCase):
    setUp=fixtures.AdapterTest.setUp
    tearDown=fixtures.AdapterTest.tearDown
    partner_proposal=fixtures.AdapterTest.partner_proposal
    approved_body=fixtures.AdapterTest.approved_body

    def test_implicit_local_owner_does_not_enable_odoo(self):
        from agntia_gestoria.auth import Actor
        from agntia_gestoria.integrations.errors import IntegrationError
        before=len(self.provider.calls)
        with patch.dict(os.environ,{'GESTORIA_OWNER_TOKEN':'','GESTORIA_ACTORS_JSON':'{}','ODOO_ALLOW_LOCAL_OWNER':'false'}):
            with self.assertRaises(IntegrationError):self.adapter.capabilities(Actor('local-owner','owner',('*',)),self.cid)
        self.assertEqual(len(self.provider.calls),before)

    def test_write_proof_is_signed_and_bound_to_database_instance(self):
        proposal=self.partner_proposal();body=self.approved_body(proposal)
        self.assertEqual(self.client.post(self.api+'/partners/commit',headers=self.owner,json=body).status_code,200)
        payload=next(p for _,method,p in self.provider.calls if method=='execute_approved')
        proof=payload['authorization'];claims=proof['claims']
        self.assertEqual(claims['instance_id'],self.server['expected_instance_id'])
        self.assertEqual(claims['company_id'],self.server['odoo_company_id'])
        expected=hmac.new(self.settings['ODOO_BRIDGE_SIGNING_KEY'].encode(),canonical(claims).encode(),hashlib.sha256).hexdigest()
        self.assertEqual(proof['signature'],expected)
        changed={**claims,'instance_id':'c'*32}
        self.assertNotEqual(proof['signature'],hmac.new(self.settings['ODOO_BRIDGE_SIGNING_KEY'].encode(),canonical(changed).encode(),hashlib.sha256).hexdigest())

    def test_concurrent_import_replay_creates_one_fact_and_one_result(self):
        preview=self.adapter.preview(self.bot,self.cid,'invoices',True,'concurrent')
        def run(_):return self.adapter.import_stages(self.bot,self.cid,preview['staging_ids'],'concurrent-key','concurrent')
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,range(2)))
        self.assertEqual(results[0],results[1])
        records=self.client.get(self.root+'/tax-records',headers=self.owner).json()
        self.assertEqual(len(records),1)


class BaselinePolicyTests(unittest.TestCase):
    def test_transport_revalidates_authority_before_retry(self):
        import httpx
        from agntia_gestoria.integrations.odoo.transport import Client,_FAILURES
        from agntia_gestoria.integrations.errors import IntegrationError
        _FAILURES.clear();requests=[];checks=[]
        client=Client(fixtures.PureTests().server(),httpx.MockTransport(lambda req:(requests.append(req) or httpx.Response(503))),lambda h,p:['192.0.2.1'],lambda _:None)
        def check():
            checks.append(True)
            if len(checks)>1:raise IntegrationError('principal_revoked','Principal revoked',403)
        client.before_request=check
        with patch.dict(os.environ,{'TEST_ODOO_KEY':'sentinel-secret-api-key'}):
            with self.assertRaises(IntegrationError) as error:client.call('res.partner','search_read',{})
        self.assertEqual(error.exception.code,'principal_revoked');self.assertEqual(len(checks),2);self.assertEqual(len(requests),1)

    def test_contract_schema_and_decimal_round_trip(self):
        from agntia_gestoria.integrations.contracts import Money,ConnectionCreate
        self.assertEqual(Money.model_validate_json(Money(amount='100.21').model_dump_json()).amount,Money(amount='100.21').amount)
        schema=ConnectionCreate.model_json_schema()
        self.assertFalse(schema['additionalProperties'])
        self.assertEqual(schema['required'],['server_ref'])
        with self.assertRaises(ValueError):ConnectionCreate(server_ref='fixture',base_url='http://169.254.169.254')

    def test_exact_approved_hash_only_and_no_fiscal_exemption(self):
        root=Path(__file__).resolve().parents[1]
        spec=importlib.util.spec_from_file_location('baseline',root/'scripts/verify_baseline.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        # An existing ADR path is required even for this isolated in-memory policy.
        adr='docs/odoo-adapter/adr/0001-batch-implementation.md'
        policy={'authorization':'Owner implementation instruction','adr':adr,'changes':{'app.py':{'old_sha256':'old','new_sha256':'new'}}}
        self.assertEqual(module.validate_changes({'app.py':'old'},{'app.py':'new'},policy),['app.py'])
        with self.assertRaises(ValueError):module.validate_changes({'app.py':'old'},{'app.py':'tampered'},policy)
        with self.assertRaises(ValueError):module.validate_changes({'app.py':'old','other.py':'a'},{'app.py':'new','other.py':'b'},policy)
        policy['changes']['agntia_gestoria/engines.py']={'old_sha256':'old','new_sha256':'new'}
        with self.assertRaises(ValueError):module.validate_changes({'app.py':'old'},{'app.py':'new'},policy)


class RegistryHardeningTests(unittest.TestCase):
    """GST-C09: la frontera que decide a qué host y con qué credencial se llama."""

    base=dict(database='agntia_test_a',api_key_env='TEST_ODOO_KEY',gestoria_company_id='a'*32,tenant_id='standalone:'+'a'*32,odoo_company_id=1,expected_instance_id='b'*32,allowed_networks=['192.0.2.0/24'])

    def load(self,base_url):
        values={'fixture':{**self.base,'base_url':base_url}}
        with patch.dict(os.environ,{'ODOO_SERVERS_JSON':json.dumps(values)}):
            return load_server('fixture')

    def test_ambiguous_numeric_hosts_are_rejected(self):
        # Cada forma resuelve a una dirección real: 2130706433 y 0x7f000001 son
        # 127.0.0.1, 017700000001 es octal de lo mismo y 127.1 es la variante corta.
        for url in ('https://2130706433','https://0x7f000001','https://017700000001','https://127.1','https://0x7f.0.0.1','https://10.0.0.1.1'):
            with self.subTest(url=url):
                with self.assertRaises(IntegrationError) as error:self.load(url)
                self.assertEqual(error.exception.code,'configuration')

    def test_canonical_literal_and_dns_name_still_load(self):
        for url in ('https://192.0.2.10','https://odoo.example.invalid','https://odoo-lab.local'):
            self.assertEqual(self.load(url).base_url,url)

    def test_credentials_must_be_header_safe(self):
        server=Server(base_url='https://odoo.example.invalid',**self.base)
        for value in ('too-short','key with spaces inside','key\twith\ttabs','k'*513):
            with self.subTest(value=value[:12]):
                with patch.dict(os.environ,{'TEST_ODOO_KEY':value}):
                    with self.assertRaises(IntegrationError) as error:credentials(server)
                    self.assertEqual(error.exception.code,'not_configured')
        with patch.dict(os.environ,{'TEST_ODOO_KEY':'k'*16}):
            self.assertEqual(credentials(server).get_secret_value(),'k'*16)
