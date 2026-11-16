import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agntia_gestoria import capabilities as capability_module
from agntia_gestoria.app import create_app
from agntia_gestoria.integrations import policy

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = {
    "GESTORIA_OWNER_TOKEN": "owner-fixture-token-12345",
    "ODOO_ADAPTER_ENABLED": "true",
    "ODOO_TEST_MODE": "true",
}


class CapabilityManifest(unittest.TestCase):
    """C01: el manifiesto declara la política real, no una promesa comercial."""

    def test_declared_capabilities_match_policy_exactly(self):
        manifest = capability_module.manifest()
        declared = {item["id"] for item in manifest["capabilities"]}
        self.assertEqual(declared, set(policy.ALL))

    def test_read_capabilities_never_mutate(self):
        for item in capability_module.manifest()["capabilities"]:
            self.assertEqual(item["mutates"], item["kind"] != "read", item["id"])
            if item["kind"] == "read":
                self.assertEqual({entry["method"] for entry in item["http"]} - {"GET"}, set(), item["id"])

    def test_roles_follow_the_policy(self):
        expected = {"read": set(capability_module.READ_ROLES), "propose": set(capability_module.PROPOSE_ROLES), "human": set(capability_module.HUMAN_ROLES)}
        for item in capability_module.manifest()["capabilities"]:
            self.assertEqual(set(item["roles"]), expected[item["kind"]], item["id"])
            self.assertEqual(item["human_approval_required"], item["kind"] == "human", item["id"])

    def test_totals_add_up(self):
        manifest = capability_module.manifest()
        totals = manifest["totals"]
        self.assertEqual(totals["capabilities"], len(manifest["capabilities"]))
        self.assertEqual(totals["read"] + totals["propose"] + totals["human"], totals["capabilities"])
        self.assertEqual(totals["read"], len(policy.READ))
        self.assertEqual(totals["propose"], len(policy.PROPOSE))
        self.assertEqual(totals["human"], len(policy.HUMAN))

    def test_every_declared_route_exists_with_its_method(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, SETTINGS):
            app = create_app(tmp)
            index = capability_module.route_index(app)
            for item in capability_module.manifest()["capabilities"]:
                for entry in item["http"]:
                    self.assertIn(entry["path"], index, item["id"])
                    self.assertIn(entry["method"], index[entry["path"]], item["id"])

    def test_internal_capabilities_do_not_claim_a_route(self):
        for item in capability_module.manifest()["capabilities"]:
            self.assertEqual(item["exposed_through"], "http" if item["http"] else "internal", item["id"])

    def test_manifest_is_json_serialisable_and_secret_free(self):
        text = json.dumps(capability_module.manifest())
        self.assertNotIn("token", text.lower())
        self.assertNotIn("secret", text.lower())
        self.assertNotIn("password", text.lower())
        parsed = json.loads(text)
        self.assertEqual(parsed["schema_version"], 1)

    def test_cli_emits_the_same_manifest(self):
        result = subprocess.run(
            [sys.executable, "-m", "agntia_gestoria.capabilities"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        printed = json.loads(result.stdout)
        self.assertEqual(printed["totals"], capability_module.manifest()["totals"])
        self.assertEqual({item["id"] for item in printed["capabilities"]}, set(policy.ALL))

    def test_manifest_rejects_drift_against_the_policy(self):
        original = policy.ALL
        try:
            policy.ALL = original | {"ghost.capability"}
            with self.assertRaises(ValueError):
                capability_module.manifest()
        finally:
            policy.ALL = original
