"""Server-side connection registry. No transport and no network side effects."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import ipaddress
import re
import sqlite3
from typing import Literal
from urllib.parse import urlsplit

from pydantic import SecretStr

from agntia_gestoria.integrations.contracts import Contract, LocalId, OdooBinding, PublicConnection, Revision, Scope
from agntia_gestoria.storage import Database, now


class RegistryError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class Principal(Contract):
    """Trusted server principal. Construct only after checking membership."""

    scope: Scope
    role: Literal["owner", "reviewer", "agent", "viewer"]


class ConnectionChange(Contract):
    connection_id: LocalId
    expected_revision: Revision


@dataclass(frozen=True)
class ResolvedConnection:
    public: PublicConnection
    origin: str = field(repr=False)
    database_name: str = field(repr=False)
    api_key: SecretStr = field(repr=False)
    odoo_company_id: int = field(repr=False)


def approved_origin(value: str, allowed_hosts: frozenset[str], allow_test_loopback: bool) -> str:
    if not value.isascii() or any(not 33 <= ord(character) <= 126 for character in value) or any(
        character in value for character in "\\%?#"
    ):
        raise ValueError("Invalid Odoo origin")
    try:
        url = urlsplit(value)
        host = url.hostname
        port = url.port
    except ValueError:
        raise ValueError("Invalid Odoo origin") from None
    if not host or url.username is not None or url.password is not None or url.path not in ("", "/") or port == 0:
        raise ValueError("Invalid Odoo origin")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None:
        if not (allow_test_loopback and url.scheme == "http" and host in ("127.0.0.1", "::1")):
            raise ValueError("Invalid Odoo origin")
    elif (
        url.scheme != "https" or host not in allowed_hosts or len(host) > 253 or "." not in host
        or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in host.split("."))
        or not re.search(r"[a-z]", host.rsplit(".", 1)[-1])
        or all(re.fullmatch(r"(?:[0-9]+|0x[0-9a-f]+)", label) for label in host.split("."))
    ):
        raise ValueError("Invalid Odoo origin")
    authority = f"[{host}]" if ":" in host else host
    if url.netloc.lower() != (f"{authority}:{port}" if port is not None else authority):
        raise ValueError("Invalid Odoo origin")
    default_port = 443 if url.scheme == "https" else 80
    suffix = f":{port}" if port is not None and port != default_port else ""
    return f"{url.scheme}://{authority}{suffix}"


class ServerCatalog:
    """Validate and snapshot configuration supplied by the service operator."""

    def __init__(
        self,
        endpoints: Mapping[str, str],
        databases: Mapping[str, str],
        credential_refs: set[str],
        read_secret: Callable[[str], str | None],
        *,
        allowed_hosts: frozenset[str],
        allow_test_loopback: bool = False,
    ):
        self._endpoints = {
            ref: approved_origin(value, allowed_hosts, allow_test_loopback) for ref, value in endpoints.items()
        }
        self._databases = dict(databases)
        self._credential_refs = frozenset(credential_refs)
        self._read_secret = read_secret
        if any(not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]{0,62}", name) for name in self._databases.values()):
            raise ValueError("Invalid Odoo database configuration")
        if (
            len(set(self._endpoints.values())) != len(self._endpoints)
            or len(set(self._databases.values())) != len(self._databases)
        ):
            raise ValueError("Duplicate Odoo configuration alias")

    def target(self, endpoint_ref: str, database_ref: str, credential_ref: str) -> tuple[str, str]:
        if credential_ref not in self._credential_refs:
            raise RegistryError("connection_unavailable")
        try:
            return self._endpoints[endpoint_ref], self._databases[database_ref]
        except KeyError:
            raise RegistryError("connection_unavailable") from None

    def secret(self, reference: str) -> SecretStr:
        if reference not in self._credential_refs:
            raise RegistryError("connection_unavailable")
        try:
            value = self._read_secret(reference)
        except Exception:
            raise RegistryError("connection_unavailable") from None
        if not isinstance(value, str) or not re.fullmatch(r"[!-~]{16,512}", value):
            raise RegistryError("connection_unavailable")
        return SecretStr(value)


def _scope_values(principal: Principal) -> tuple[str, str]:
    return principal.scope.tenant_id, principal.scope.gestoria_company_id


def _scoped_row(connection: sqlite3.Connection, principal: Principal, connection_id: str) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM odoo_connections WHERE tenant_id = ? AND company_id = ? AND id = ?",
        (*_scope_values(principal), connection_id),
    ).fetchone()
    if row is None:
        raise RegistryError("not_found")
    return row


def _public(row: sqlite3.Row, scope: Scope) -> PublicConnection:
    return PublicConnection(
        connection_id=row["id"], scope=scope, state=row["state"], created_at=row["created_at"],
        revision=row["revision"],
    )


class ConnectionRegistry:
    def __init__(self, database: Database, catalog: ServerCatalog):
        self.database = database
        self.catalog = catalog

    def register(self, principal: Principal, binding: OdooBinding) -> PublicConnection:
        if principal.role != "owner":
            raise RegistryError("denied")
        if principal.scope != binding.scope:
            raise RegistryError("not_found")
        with self.database.transaction() as connection:
            scope = _scope_values(principal)
            if not connection.execute(
                "SELECT 1 FROM odoo_company_scopes WHERE tenant_id = ? AND company_id = ?", scope
            ).fetchone():
                raise RegistryError("not_found")
            self.catalog.target(binding.endpoint_ref, binding.database_ref, binding.credential_ref)
            try:
                connection.execute(
                    """
                    INSERT INTO odoo_connections(
                        id, tenant_id, company_id, endpoint_ref, database_ref, credential_ref, odoo_company_id,
                        state, revision, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_validation', 0, ?)
                    """,
                    (
                        binding.connection_id, *scope, binding.endpoint_ref, binding.database_ref,
                        binding.credential_ref, binding.odoo_company_id, now(),
                    ),
                )
            except sqlite3.IntegrityError:
                raise RegistryError("connection_conflict") from None
            return _public(_scoped_row(connection, principal, binding.connection_id), principal.scope)

    def get(self, principal: Principal, connection_id: str) -> PublicConnection:
        with self.database.connection() as connection:
            return _public(_scoped_row(connection, principal, connection_id), principal.scope)

    def change(
        self, principal: Principal, change: ConnectionChange, *, credential_ref: str | None
    ) -> PublicConnection:
        """Rotate the credential reference, or disable when no replacement is given."""
        if principal.role != "owner":
            raise RegistryError("denied")
        with self.database.transaction() as connection:
            row = _scoped_row(connection, principal, change.connection_id)
            if row["revision"] != change.expected_revision:
                raise RegistryError("revision_conflict")
            if credential_ref is None:
                credential_ref = row["credential_ref"]
                state = "disabled"
            else:
                if row["state"] == "disabled":
                    raise RegistryError("connection_unavailable")
                self.catalog.target(row["endpoint_ref"], row["database_ref"], credential_ref)
                state = "pending_validation"
            connection.execute(
                """
                UPDATE odoo_connections SET credential_ref = ?, state = ?, revision = revision + 1
                WHERE tenant_id = ? AND company_id = ? AND id = ? AND revision = ?
                """,
                (credential_ref, state, *_scope_values(principal), change.connection_id, change.expected_revision),
            )
            return _public(_scoped_row(connection, principal, change.connection_id), principal.scope)

    def resolve_read(self, principal: Principal, connection_id: str) -> ResolvedConnection:
        with self.database.connection() as connection:
            row = _scoped_row(connection, principal, connection_id)
            if row["state"] != "active":
                raise RegistryError("connection_unavailable")
        origin, database = self.catalog.target(row["endpoint_ref"], row["database_ref"], row["credential_ref"])
        return ResolvedConnection(
            public=_public(row, principal.scope), origin=origin, database_name=database,
            api_key=self.catalog.secret(row["credential_ref"]), odoo_company_id=row["odoo_company_id"],
        )
