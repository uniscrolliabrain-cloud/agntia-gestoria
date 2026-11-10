import tempfile
import unittest

from agntia_gestoria.integrations.contracts import OdooBinding, Scope
from agntia_gestoria.integrations.migrations import migrate
from agntia_gestoria.integrations.registry import (
    ConnectionChange,
    ConnectionRegistry,
    Principal,
    RegistryError,
    ServerCatalog,
    approved_origin,
)
from agntia_gestoria.storage import Database


COMPANY = "a" * 32
OTHER = "b" * 32
CONNECTION = "c" * 32
HOST = "odoo.lab.example"
SECRET = "synthetic-api-key-guard-001"


class OdooRegistryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = Database(directory.name)
        migrate(self.db)
        with self.db.transaction() as connection:
            connection.executemany("INSERT INTO companies VALUES (?, '{}')", [(COMPANY,), (OTHER,)])
            connection.executemany(
                "INSERT INTO odoo_company_scopes VALUES (?, ?)", [(COMPANY, "tenant-a"), (OTHER, "tenant-b")],
            )
        self.secret_calls = []
        self.catalog = ServerCatalog(
            {"endpoint-a": f"https://{HOST}:443/"}, {"db-a": "synthetic_a"}, {"key-a", "key-b"},
            self.read_secret, allowed_hosts=frozenset({HOST}),
        )
        self.registry = ConnectionRegistry(self.db, self.catalog)
        self.scope = Scope(tenant_id="tenant-a", gestoria_company_id=COMPANY)
        self.owner = Principal(scope=self.scope, role="owner")
        self.viewer = Principal(scope=self.scope, role="viewer")
        self.other = Principal(scope=Scope(tenant_id="tenant-b", gestoria_company_id=OTHER), role="owner")
        self.binding = OdooBinding(
            scope=self.scope, connection_id=CONNECTION, endpoint_ref="endpoint-a",
            database_ref="db-a", credential_ref="key-a", odoo_company_id=10,
        )

    def read_secret(self, reference):
        self.secret_calls.append(reference)
        return SECRET if reference == "key-a" else "invalid\nheader"

    def activate_fixture(self):
        with self.db.transaction() as connection:
            connection.execute("UPDATE odoo_connections SET state = 'active' WHERE id = ?", (CONNECTION,))

    def test_scope_and_state_are_checked_before_secret_lookup(self):
        public = self.registry.register(self.owner, self.binding)
        self.assertEqual(public.state, "pending_validation")
        for principal, error in ((self.owner, "connection_unavailable"), (self.other, "not_found")):
            with self.assertRaisesRegex(RegistryError, error):
                self.registry.resolve_read(principal, CONNECTION)
        self.assertEqual(self.secret_calls, [])
        self.activate_fixture()
        with self.assertRaisesRegex(RegistryError, "not_found"):
            self.registry.resolve_read(self.other, CONNECTION)
        self.assertEqual(self.secret_calls, [])
        resolved = self.registry.resolve_read(self.viewer, CONNECTION)
        self.assertEqual(resolved.origin, f"https://{HOST}")
        self.assertEqual(resolved.api_key.get_secret_value(), SECRET)
        self.assertEqual(self.secret_calls, ["key-a"])
        for token in (SECRET, "synthetic_a", "key-a", HOST):
            self.assertNotIn(token, repr(resolved))
            self.assertNotIn(token, resolved.public.model_dump_json())
        with self.db.connection() as connection:
            self.assertNotIn(SECRET, repr([tuple(row) for row in connection.execute("SELECT * FROM odoo_connections")]))

    def test_scope_role_and_target_duplicates(self):
        with self.assertRaisesRegex(RegistryError, "denied"):
            self.registry.register(self.viewer, self.binding)
        with self.assertRaisesRegex(RegistryError, "not_found"):
            self.registry.register(self.other, self.binding)
        self.registry.register(self.owner, self.binding)
        with self.assertRaisesRegex(RegistryError, "connection_conflict"):
            self.registry.register(self.other, self.binding.model_copy(update={
                "scope": self.other.scope, "connection_id": "d" * 32,
            }))
        self.assertEqual(self.secret_calls, [])

    def test_rotation_invalidates_and_disable_rejects_reads(self):
        self.registry.register(self.owner, self.binding)
        self.activate_fixture()
        first = ConnectionChange(connection_id=CONNECTION, expected_revision=0)
        with self.assertRaisesRegex(RegistryError, "denied"):
            self.registry.change(self.viewer, first, credential_ref="key-b")
        rotated = self.registry.change(self.owner, first, credential_ref="key-b")
        self.assertEqual((rotated.state, rotated.revision), ("pending_validation", 1))
        with self.assertRaisesRegex(RegistryError, "revision_conflict"):
            self.registry.change(self.owner, first, credential_ref=None)
        with self.assertRaisesRegex(RegistryError, "connection_unavailable"):
            self.registry.resolve_read(self.viewer, CONNECTION)
        self.assertEqual(self.secret_calls, [])
        self.activate_fixture()
        with self.assertRaisesRegex(RegistryError, "^connection_unavailable$"):
            self.registry.resolve_read(self.viewer, CONNECTION)
        self.assertEqual(self.secret_calls, ["key-b"])
        second = ConnectionChange(connection_id=CONNECTION, expected_revision=1)
        self.assertEqual(self.registry.change(self.owner, second, credential_ref=None).state, "disabled")
        with self.assertRaisesRegex(RegistryError, "connection_unavailable"):
            self.registry.resolve_read(self.viewer, CONNECTION)
        self.assertEqual(self.secret_calls, ["key-b"])

    def test_approved_origin_configuration_rejects_ambiguous_endpoints(self):
        allow = frozenset({HOST, "127.0.0.1", "0x7f.0x0.0x0.0x1"})
        self.assertEqual(approved_origin(f"https://{HOST}:443/", allow, False), f"https://{HOST}")
        for origin in [
            f"http://{HOST}", f"https://{HOST}/path", f"https://{HOST}?", f"https://{HOST}#",
            f"https://{HOST}:0", f"https://{HOST}:", f"https://{HOST}:0443", f"https://{HOST}:99999",
            f"https://{HOST}%00", f"https://{HOST}\\x",
            f"https://user@{HOST}", f"\x00https://{HOST}", "https://unlisted.example",
            "https://127.0.0.1", "http://127.0.0.1:8069", "https://0x7f.0x0.0x0.0x1",
        ]:
            with self.subTest(origin=origin), self.assertRaisesRegex(ValueError, "^Invalid Odoo origin$"):
                approved_origin(origin, allow, False)
        self.assertEqual(approved_origin("http://127.0.0.1:8069", allow, True), "http://127.0.0.1:8069")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            ServerCatalog({"a": f"https://{HOST}", "b": f"https://{HOST}:443/"}, {}, set(), self.read_secret, allowed_hosts=allow)

    def test_secret_backend_failure_has_stable_public_error(self):
        def failed_provider(reference):
            raise RuntimeError(SECRET)

        catalog = ServerCatalog({}, {}, {"key-a"}, failed_provider, allowed_hosts=frozenset())
        with self.assertRaisesRegex(RegistryError, "^connection_unavailable$") as failure:
            catalog.secret("key-a")
        self.assertTrue(failure.exception.__suppress_context__)
