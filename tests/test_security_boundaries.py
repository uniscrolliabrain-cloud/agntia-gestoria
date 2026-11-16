import json
import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from agntia_gestoria.app import create_app

OWNER = "owner-fixture-token-12345"
SENTINEL = "sentinel-api-key-never-log-this"


def company_payload(name):
    return {
        "name": name,
        "legal_form": "autonomo",
        "tax_territory": "common",
        "nif": "ESB00000000",
        "facts": {
            "vat_status": "liable",
            "vat_return_required": True,
            "vat_periodicity": "quarterly",
            "irpf_payment_model": "130",
        },
    }


class Boundaries(unittest.TestCase):
    """C02: aislamiento entre empresas, fail-closed y ausencia de fugas."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = {
            "GESTORIA_OWNER_TOKEN": OWNER,
            "ODOO_ADAPTER_ENABLED": "true",
            "ODOO_TEST_MODE": "true",
            "ODOO_BOT_KEY": SENTINEL,
        }
        self.env = patch.dict(os.environ, self.settings)
        self.env.start()
        self.client = TestClient(create_app(self.tmp.name))
        self.owner = {"Authorization": "Bearer " + OWNER}
        first = self.client.post("/api/companies", headers=self.owner, json=company_payload("Empresa alfa"))
        second = self.client.post("/api/companies", headers=self.owner, json=company_payload("Empresa beta"))
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.alpha = first.json()["id"]
        self.beta = second.json()["id"]

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.tmp.cleanup()

    def viewer_of(self, company_id, actor_id="viewer-alfa", role="viewer"):
        token = f"{actor_id}-fixture-token-12345"
        return token, {"Authorization": "Bearer " + token}, {
            "GESTORIA_ACTORS_JSON": json.dumps({token: {"id": actor_id, "role": role, "companies": [company_id]}})
        }

    def test_company_of_another_actor_is_not_found(self):
        _, headers, extra = self.viewer_of(self.alpha)
        with patch.dict(os.environ, extra):
            self.assertEqual(self.client.get(f"/api/companies/{self.alpha}", headers=headers).status_code, 200)
            foreign = self.client.get(f"/api/companies/{self.beta}", headers=headers)
        self.assertEqual(foreign.status_code, 404)
        self.assertNotIn(self.beta, foreign.text)

    def test_case_of_another_company_is_invisible(self):
        created = self.client.post(
            f"/api/companies/{self.alpha}/cases",
            headers=self.owner,
            json={"title": "Expediente alfa", "description": "Solo empresa alfa"},
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]
        _, headers, extra = self.viewer_of(self.alpha)
        with patch.dict(os.environ, extra):
            self.assertEqual(self.client.get(f"/api/companies/{self.alpha}/cases/{case_id}", headers=headers).status_code, 200)
            foreign = self.client.get(f"/api/companies/{self.beta}/cases/{case_id}", headers=headers)
        self.assertEqual(foreign.status_code, 404)

    def test_actor_cannot_write_into_a_foreign_company(self):
        _, headers, extra = self.viewer_of(self.alpha)
        with patch.dict(os.environ, extra):
            forbidden = self.client.post(
                f"/api/companies/{self.beta}/cases",
                headers=headers,
                json={"title": "Intento ajeno", "description": "Sin acceso"},
            )
        # El rol se comprueba antes que la empresa: 403 por rol, 404 si el actor
        # tuviera rol suficiente. Ninguno de los dos revela datos ajenos.
        self.assertIn(forbidden.status_code, (403, 404))
        own = self.client.get(f"/api/companies/{self.beta}/cases", headers=self.owner)
        self.assertEqual(own.status_code, 200)
        self.assertFalse([case for case in own.json() if case.get("title") == "Intento ajeno"])

    def test_odoo_route_requires_credentials(self):
        response = self.client.get(f"/api/companies/{self.alpha}/integrations/odoo/conflicts")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], "auth")
        self.assertNotIn(SENTINEL, response.text)

    def test_adapter_disabled_is_fail_closed(self):
        with patch.dict(os.environ, {"ODOO_ADAPTER_ENABLED": "false"}):
            response = self.client.get(f"/api/companies/{self.alpha}/integrations/odoo/conflicts", headers=self.owner)
        self.assertEqual(response.status_code, 424)
        self.assertEqual(response.json()["code"], "disabled")

    def test_error_payload_and_audit_never_leak_the_key(self):
        response = self.client.get(f"/api/companies/{self.alpha}/integrations/odoo/conflicts", headers=self.owner)
        self.assertIn(response.status_code, (404, 424, 503), response.text)
        self.assertNotIn(SENTINEL, response.text)
        exported = self.client.get(f"/api/companies/{self.alpha}/export", headers=self.owner)
        self.assertEqual(exported.status_code, 200)
        self.assertNotIn(SENTINEL, exported.text)

    def test_malformed_json_is_a_typed_validation_error(self):
        response = self.client.post(
            f"/api/companies/{self.alpha}/integrations/odoo/connections",
            headers={**self.owner, "Content-Type": "application/json"},
            content="{",
        )
        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertEqual(body["code"], "validation")
        self.assertIn("correlation_id", body)

    def test_security_headers_are_present(self):
        response = self.client.get("/health/live")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertIn("default-src 'self'", response.headers.get("Content-Security-Policy", ""))

    def test_remote_access_without_configuration_is_refused(self):
        with patch.dict(os.environ, {"GESTORIA_OWNER_TOKEN": "", "GESTORIA_ACTORS_JSON": "{}", "GESTORIA_ALLOW_LOCAL_OWNER": "false"}):
            response = self.client.get("/api/companies")
        self.assertEqual(response.status_code, 403)
