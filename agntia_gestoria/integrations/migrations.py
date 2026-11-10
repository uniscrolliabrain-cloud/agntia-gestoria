"""Opt-in SQLite migrations for the Odoo integration."""

from contextlib import closing
import hashlib
import os
from pathlib import Path
import sqlite3
import tempfile

from agntia_gestoria.storage import Database


MIGRATIONS = (
    (
        """
        CREATE TABLE odoo_company_scopes (
            company_id TEXT PRIMARY KEY NOT NULL REFERENCES companies(id),
            tenant_id TEXT NOT NULL,
            UNIQUE (tenant_id, company_id)
        )
        """,
        """
        CREATE TABLE odoo_connections (
            id TEXT PRIMARY KEY NOT NULL,
            tenant_id TEXT NOT NULL,
            company_id TEXT NOT NULL,
            endpoint_ref TEXT NOT NULL,
            database_ref TEXT NOT NULL,
            credential_ref TEXT NOT NULL,
            odoo_company_id INTEGER NOT NULL CHECK (typeof(odoo_company_id) = 'integer' AND odoo_company_id BETWEEN 1 AND 2147483647),
            state TEXT NOT NULL CHECK (state IN ('pending_validation', 'active', 'disabled')),
            revision INTEGER NOT NULL CHECK (typeof(revision) = 'integer' AND revision BETWEEN 0 AND 2147483647),
            created_at TEXT NOT NULL,
            UNIQUE (tenant_id, company_id, id),
            UNIQUE (endpoint_ref, database_ref, odoo_company_id),
            FOREIGN KEY (tenant_id, company_id) REFERENCES odoo_company_scopes(tenant_id, company_id)
        )
        """,
        """
        CREATE TABLE odoo_sync_cursors (
            tenant_id TEXT NOT NULL,
            company_id TEXT NOT NULL,
            connection_id TEXT NOT NULL,
            model TEXT NOT NULL CHECK (model IN ('res.partner', 'account.move', 'account.move.line', 'ir.attachment')),
            write_date TEXT NOT NULL,
            remote_id INTEGER NOT NULL CHECK (typeof(remote_id) = 'integer' AND remote_id BETWEEN 1 AND 2147483647),
            PRIMARY KEY (tenant_id, company_id, connection_id, model),
            FOREIGN KEY (tenant_id, company_id, connection_id)
                REFERENCES odoo_connections(tenant_id, company_id, id)
        )
        """,
        """
        CREATE TABLE odoo_contact_operations (
            id TEXT PRIMARY KEY NOT NULL,
            tenant_id TEXT NOT NULL,
            company_id TEXT NOT NULL,
            connection_id TEXT NOT NULL,
            connection_revision INTEGER NOT NULL CHECK (typeof(connection_revision) = 'integer' AND connection_revision BETWEEN 0 AND 2147483647),
            idempotency_key TEXT NOT NULL,
            preview_id TEXT NOT NULL,
            preview_hash TEXT NOT NULL,
            approval_id TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            correlation_id TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN ('pending', 'in_flight', 'succeeded', 'rejected', 'reconciliation_required')),
            remote_id INTEGER CHECK (remote_id IS NULL OR (typeof(remote_id) = 'integer' AND remote_id BETWEEN 1 AND 2147483647)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            CHECK ((state = 'succeeded') = (remote_id IS NOT NULL)),
            UNIQUE (tenant_id, company_id, connection_id, idempotency_key),
            FOREIGN KEY (tenant_id, company_id, connection_id)
                REFERENCES odoo_connections(tenant_id, company_id, id)
        )
        """,
    ),
)


def _apply(connection: sqlite3.Connection, migrations: tuple[tuple[str, ...], ...]) -> int:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS odoo_schema_migrations (
            version INTEGER PRIMARY KEY CHECK (version > 0),
            checksum TEXT NOT NULL
        )
    """)
    expected = [
        (version, hashlib.sha256("\0".join(statements).encode()).hexdigest())
        for version, statements in enumerate(migrations, start=1)
    ]
    applied = [
        tuple(row) for row in connection.execute(
            "SELECT version, checksum FROM odoo_schema_migrations ORDER BY version"
        )
    ]
    if applied != expected[:len(applied)]:
        raise RuntimeError("Incompatible Odoo migration history")
    for version, checksum in expected[len(applied):]:
        for statement in migrations[version - 1]:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO odoo_schema_migrations(version, checksum) VALUES (?, ?)", (version, checksum)
        )
    return len(expected)


def migrate(database: Database) -> int:
    """Apply the missing migrations atomically under the existing write lock."""
    with database.transaction() as connection:
        return _apply(connection, MIGRATIONS)


def backup(database: Database, destination: Path) -> Path:
    """Publish a consistent SQLite backup without overwriting an existing file."""
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    fd, filename = tempfile.mkstemp(prefix=".odoo-backup-", dir=destination.parent)
    os.close(fd)
    temporary = Path(filename)
    try:
        with database.connection() as source, closing(sqlite3.connect(temporary)) as target:
            source.backup(target)
            if target.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise RuntimeError("SQLite backup integrity check failed")
        # The hard link publishes a complete backup and fails if another caller won.
        os.link(temporary, destination)
        return destination
    finally:
        temporary.unlink()
