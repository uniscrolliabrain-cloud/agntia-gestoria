import json
import os
import tempfile
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from agntia_gestoria.app import create_app
from agntia_gestoria.integrations import delegation

OWNER = "owner-fixture-token-12345"
KEY = "clave-de-delegacion-sintetica-para-pruebas-0123456789"


def company_payload(name):
    return {
        "name": name,
        "legal_form": "autonomo",
        "tax_territory": "common",
        "nif": "ESB00000000",
        "facts": {"vat_status": "liable", "vat_return_required": True, "vat_periodicity": "quarterly", "irpf_payment_model": "130"},
    }


class DelegatedIdentity(unittest.TestCase):
    """C03: la autoridad delegada se verifica en servidor y no se puede escalar."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = {
            "GESTORIA_OWNER_TOKEN": OWNER,
            "ODOO_ADAPTER_ENABLED": "true",
            "ODOO_TEST_MODE": "true",
            "GESTORIA_DELEGATION_KEY": KEY,
            "ODOO_IDENTITY_MODE": "integrated",
        }
        self.env = patch.dict(os.environ, self.settings)
        self.env.start()
        self.client = TestClient(create_app(self.tmp.name))
        self.owner = {"Authorization": "Bearer " + OWNER}
        self.alpha = self.client.post("/api/companies", headers=self.owner, json=company_payload("Empresa alfa")).json()["id"]
        self.beta = self.client.post("/api/companies", headers=self.owner, json=company_payload("Empresa beta")).json()["id"]

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.tmp.cleanup()

    def claims(self, **overrides):
        now = int(time.time())
        base = {
            "schema": 1,
            "iss": "agente",
            "aud": "gestoria",
            "sub": "agent-alfa",
            "role": "agent",
            "tenant": "tenant-alfa",
            "companies": [self.alpha],
            "capabilities": ["health", "conflicts.read", "events.read"],
            "delegator": "founder",
            "iat": now - 5,
            "exp": now + 300,
        }
        base.update(overrides)
        return base

    def assertion(self, key=KEY, **overrides):
        return delegation.sign(self.claims(**overrides), key)

    def odoo(self, cid=None, headers=None, path="/conflicts", method="get", **kwargs):
        preset = {"X-Agente-Delegation": self.assertion()}
        preset.update(headers or {})
        return getattr(self.client, method)(f"/api/companies/{cid or self.alpha}/integrations/odoo{path}", headers=preset, **kwargs)

    def test_valid_assertion_is_accepted(self):
        response = self.odoo()
        self.assertNotEqual(response.status_code, 401, response.text)
        self.assertIn(response.status_code, (404, 424, 503), response.text)

    def test_tampered_payload_is_rejected(self):
        assertion = self.assertion()
        payload, signature = assertion.split(".")
        forged = delegation._encode(json.dumps(self.claims(sub="intruso")).encode())
        response = self.odoo(headers={"X-Agente-Delegation": forged + "." + signature})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], "unsafe_principal")

    def test_expired_assertion_is_rejected(self):
        expired = self.assertion(exp=int(time.time()) - 1, iat=int(time.time()) - 600)
        response = self.odoo(headers={"X-Agente-Delegation": expired})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], "principal_revoked")

    def test_wrong_audience_and_issuer_are_rejected(self):
        for override in ({"aud": "otro-servicio"}, {"iss": "desconocido"}):
            with self.subTest(override=override):
                response = self.odoo(headers={"X-Agente-Delegation": self.assertion(**override)})
                self.assertEqual(response.status_code, 401)

    def test_delegation_cannot_claim_owner_role(self):
        response = self.odoo(headers={"X-Agente-Delegation": self.assertion(role="owner")})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], "unsafe_principal")

    def test_capability_outside_policy_is_forbidden(self):
        response = self.odoo(headers={"X-Agente-Delegation": self.assertion(capabilities=["health", "payments.send"])})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["code"], "forbidden")

    def test_capability_not_delegated_is_forbidden(self):
        response = self.odoo(path="/partners/commit", method="post", json={"proposal_id": "a" * 32, "approval_id": "b" * 32, "expected_revision": 0, "idempotency_key": "key-de-prueba-0001"})
        self.assertEqual(response.status_code, 403, response.text)
        self.assertIn("no incluye esta capacidad", response.text)

    def test_foreign_company_is_not_found(self):
        response = self.odoo(cid=self.beta)
        self.assertEqual(response.status_code, 404)

    def test_rotated_key_revokes_previous_assertions(self):
        stale = self.assertion()
        rotated = "otra-clave-de-delegacion-sintetica-para-pruebas-9876543210"
        with patch.dict(os.environ, {"GESTORIA_DELEGATION_KEY": rotated}):
            response = self.odoo(headers={"X-Agente-Delegation": stale})
        self.assertEqual(response.status_code, 401)

    def test_missing_configuration_is_fail_closed(self):
        with patch.dict(os.environ, {"GESTORIA_DELEGATION_KEY": ""}):
            response = self.odoo()
        self.assertEqual(response.status_code, 424)
        self.assertEqual(response.json()["code"], "not_configured")

    def test_oversized_assertion_is_rejected(self):
        response = self.odoo(headers={"X-Agente-Delegation": "a" * 5000})
        self.assertEqual(response.status_code, 401)

    def test_local_token_still_works_for_odoo_routes(self):
        response = self.client.get(f"/api/companies/{self.alpha}/integrations/odoo/conflicts", headers=self.owner)
        self.assertNotEqual(response.status_code, 401, response.text)
