from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from agntia_gestoria.integrations.migrations import _apply, backup, migrate
from agntia_gestoria.storage import Database


COMPANY = "a" * 32
OTHER_COMPANY = "b" * 32
CONTACT = "c" * 32
CONNECTION = "d" * 32
NOW = "2026-11-10T12:30:00Z"


class OdooMigrationsTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.database = Database(directory.name)
        self.backup_path = Path(directory.name) / "backup.sqlite3"
        with self.database.transaction() as connection:
            connection.executemany(
                "INSERT INTO companies(id, body) VALUES (?, ?)", [(COMPANY, "{}"), (OTHER_COMPANY, "{}")]
            )
            obj = {"id": CONTACT, "name": "Synthetic existing record"}
            self.database.put(connection, COMPANY, "case", obj)
            self.database.audit(
                connection, COMPANY, SimpleNamespace(id="actor", role="owner"), "case.created", CONTACT, obj,
            )

    def legacy_snapshot(self, connection):
        tables = ("companies", "objects", "audit")
        return {table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY rowid")] for table in tables}

    def tables(self, connection):
        return {row[0] for row in connection.execute("SELECT name FROM sqlite_schema WHERE type = 'table'")}

    def test_backup_and_upgrade_preserve_legacy_audit(self):
        with self.database.connection() as connection:
            before = self.legacy_snapshot(connection)
        self.assertEqual(backup(self.database, self.backup_path), self.backup_path)
        with self.assertRaises(FileExistsError):
            backup(self.database, self.backup_path)
        self.assertEqual(migrate(self.database), 1)
        self.assertEqual(migrate(self.database), 1)
        with closing(sqlite3.connect(self.backup_path)) as restored, self.database.connection() as upgraded:
            self.assertEqual(self.legacy_snapshot(restored), before)
            self.assertEqual(self.legacy_snapshot(upgraded), before)
            self.assertNotIn("odoo_schema_migrations", self.tables(restored))
            self.assertEqual(upgraded.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            self.assertEqual(upgraded.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_failed_migration_rolls_back_ddl_and_ledger(self):
        with self.assertRaises(sqlite3.OperationalError):
            with self.database.transaction() as connection:
                _apply(connection, (("CREATE TABLE test_step(id INTEGER)", "SELECT * FROM nonexistent"),))
        with self.database.connection() as connection:
            self.assertNotIn("test_step", self.tables(connection))
            self.assertNotIn("odoo_schema_migrations", self.tables(connection))
        self.assertEqual(migrate(self.database), 1)

    def test_checksum_mismatch_rejected_without_rewrite(self):
        migrate(self.database)
        with self.database.transaction() as connection:
            connection.execute("UPDATE odoo_schema_migrations SET checksum = 'different'")
        with self.assertRaisesRegex(RuntimeError, "Incompatible Odoo migration history"):
            migrate(self.database)
        with self.database.connection() as connection:
            self.assertEqual(connection.execute("SELECT checksum FROM odoo_schema_migrations").fetchone()[0], "different")

    def test_concurrent_startup_applies_migration_once(self):
        with ThreadPoolExecutor(max_workers=4) as workers:
            self.assertEqual(list(workers.map(migrate, [self.database] * 4)), [1] * 4)
        with self.database.connection() as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM odoo_schema_migrations").fetchone()[0], 1)

    def test_scoped_fk_and_idempotency_state(self):
        migrate(self.database)
        with self.database.transaction() as connection:
            connection.executemany(
                "INSERT INTO odoo_company_scopes VALUES (?, ?)",
                [(COMPANY, "tenant-a"), (OTHER_COMPANY, "tenant-b")],
            )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO odoo_company_scopes VALUES (?, ?)", (COMPANY, "tenant-b"))
            connection.execute(
                "INSERT INTO odoo_connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (CONNECTION, "tenant-a", COMPANY, "endpoint-ref", "db-ref", "credential-ref", 1, "active", 0, NOW),
            )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO odoo_connections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("9" * 32, "tenant-b", OTHER_COMPANY, "endpoint-ref", "db-ref", "other-ref", 1, "active", 0, NOW),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO odoo_sync_cursors VALUES (?, ?, ?, ?, ?, ?)",
                    ("tenant-b", OTHER_COMPANY, CONNECTION, "res.partner", NOW, 10),
                )
            statement = "INSERT INTO odoo_contact_operations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            operation = (
                "e" * 32, "tenant-a", COMPANY, CONNECTION, 0, "request-1", "f" * 32, "sha256:" + "0" * 64,
                "1" * 32, "owner-a", "correlation-1", "reconciliation_required", None, NOW, NOW,
            )
            connection.execute(statement, operation)
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(statement, ("2" * 32, *operation[1:]))
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE odoo_contact_operations SET state = 'succeeded'")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE odoo_contact_operations SET remote_id = 9")
            connection.execute("UPDATE odoo_contact_operations SET state = 'succeeded', remote_id = 9")
