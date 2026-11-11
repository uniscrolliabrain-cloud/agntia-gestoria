from contextlib import contextmanager
import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from agntia_gestoria.app import create_app
from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.odoo.service import GuardedClient
from agntia_gestoria.storage import Database


TOKEN = "synthetic-owner-token-123456"


class DeliveryHardeningTests(unittest.TestCase):
    def test_local_owner_requires_explicit_configuration(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            "GESTORIA_OWNER_TOKEN": "", "GESTORIA_ACTORS_JSON": "{}", "GESTORIA_ALLOW_LOCAL_OWNER": "false",
        }):
            with TestClient(create_app(folder), client=("127.0.0.1", 1234)) as client:
                self.assertEqual(client.get("/api/status").status_code, 403)
                with patch.dict(os.environ, {"GESTORIA_ALLOW_LOCAL_OWNER": "true"}):
                    self.assertEqual(client.get("/api/status").status_code, 200)

    def test_opaque_session_logout_expiration_and_token_rotation(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            "GESTORIA_OWNER_TOKEN": TOKEN, "GESTORIA_ACTORS_JSON": "{}",
        }):
            app = create_app(folder)
            with TestClient(app) as client:
                self.assertEqual(client.post("/api/login", json={"token": TOKEN}).status_code, 200)
                cookie = client.cookies["gestoria_session"]
                self.assertNotEqual(cookie, TOKEN)
                self.assertEqual(client.get("/api/status").status_code, 200)
                self.assertEqual(client.post("/api/logout").status_code, 200)
                client.cookies.set("gestoria_session", cookie)
                self.assertEqual(client.get("/api/status").status_code, 401)
                client.cookies.clear()
                client.post("/api/login", json={"token": TOKEN})
                with app.state.db.transaction() as connection:
                    connection.execute("UPDATE browser_sessions SET expires_at=0")
                self.assertEqual(client.get("/api/status").status_code, 401)
                client.cookies.clear()
                client.post("/api/login", json={"token": TOKEN})
                with patch.dict(os.environ, {"GESTORIA_OWNER_TOKEN": TOKEN + "-rotated"}):
                    self.assertEqual(client.get("/api/status").status_code, 401)

    def test_login_limit_and_public_origin(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            "GESTORIA_OWNER_TOKEN": TOKEN, "GESTORIA_ACTORS_JSON": "{}",
            "GESTORIA_PUBLIC_ORIGIN": "https://gestoria.example",
        }):
            with TestClient(create_app(folder)) as client:
                self.assertEqual(client.post("/api/login", headers={
                    "Host": "attacker.example", "Origin": "http://attacker.example",
                }, json={"token": TOKEN}).status_code, 403)
                accepted = client.post("/api/login", headers={"Origin": "https://gestoria.example"}, json={"token": TOKEN})
                self.assertIn("Secure", accepted.headers["set-cookie"])
                for _ in range(9):
                    self.assertEqual(client.post("/api/login", json={"token": "wrong-secret-token-12345"}).status_code, 401)
                self.assertEqual(client.post("/api/login", json={"token": TOKEN}).status_code, 429)

    def test_put_preserves_scope_and_updates_unique_key(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Database(folder)
            a, b, oid = "a"*32, "b"*32, "c"*32
            with db.transaction() as connection:
                connection.executemany("INSERT INTO companies VALUES(?,?)", [(a, "{}"), (b, "{}")])
                db.put(connection, a, "case", {"id": oid, "title": "original"}, "first")
                with self.assertRaises(FileNotFoundError):
                    db.put(connection, b, "case", {"id": oid, "title": "foreign"})
                with self.assertRaises(FileNotFoundError):
                    db.put(connection, a, "document", {"id": oid})
                self.assertEqual(db.get(connection, a, oid, "case")["title"], "original")
                db.put(connection, a, "case", {"id": oid, "title": "updated"}, "second")
                db.put(connection, a, "case", {"id": oid, "title": "retained"})
                self.assertEqual(connection.execute("SELECT unique_key FROM objects").fetchone()[0], "second")

    def test_metric_failure_preserves_success_and_original_provider_error(self):
        class BrokenDB:
            @contextmanager
            def transaction(self):
                raise sqlite3.OperationalError("synthetic metrics failure")
                yield

        class Service:
            db = BrokenDB()
            failure = None

            def scope(self, *args):
                return {"id": "connection"}, None

            def client_factory(self, server):
                return self

            def call(self, *args):
                if self.failure:
                    raise self.failure
                return {"ok": True}

        service = Service()
        client = GuardedClient(service, None, "company", {"id": "connection"}, "contacts.read")
        self.assertEqual(client.call("res.partner", "search_read"), {"ok": True})
        service.failure = IntegrationError("timeout", "synthetic timeout", 504, True)
        with self.assertRaises(IntegrationError) as failure:
            client.call("res.partner", "search_read")
        self.assertIs(failure.exception, service.failure)

    def test_error_action_respects_uncertainty(self):
        uncertain = IntegrationError("network", "safe", 503, True, True).public()
        self.assertEqual(uncertain["next_action"], "reconcile_write")
        self.assertFalse(uncertain["retryable"])
        self.assertEqual(IntegrationError("timeout", "safe", 504, True, False).public()["next_action"], "retry_later")
