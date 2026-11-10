"""Read and staging contracts for Odoo. No transport or authorization here."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, BeforeValidator, ConfigDict, Field, TypeAdapter

from agntia_gestoria.models import Model


def require_timestamp(value: object) -> object:
    if not isinstance(value, (str, datetime)):
        raise ValueError("Use an ISO 8601 timestamp with timezone")
    if isinstance(value, str) and (
        len(value) < 20 or value[10] != "T" or value[13] != ":" or value[16] != ":"
    ):
        raise ValueError("Use an ISO 8601 timestamp with timezone")
    return value


def require_version(value: object) -> object:
    if type(value) is not int or value != 1:
        raise ValueError("Unsupported schema version")
    return value


Timestamp = Annotated[AwareDatetime, BeforeValidator(require_timestamp)]
SchemaVersion = Annotated[Literal[1], BeforeValidator(require_version)]
LocalId = Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{32}$")]
OpaqueId = Annotated[str, Field(strict=True, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")]
RemoteId = Annotated[int, Field(strict=True, gt=0, le=2_147_483_647)]
Revision = Annotated[int, Field(strict=True, ge=0, le=2_147_483_647)]
Digest = Annotated[str, Field(strict=True, pattern=r"^sha256:[0-9a-f]{64}$")]
PageSize = Annotated[int, Field(strict=True, ge=1, le=200)]
RemoteModel = Literal["res.partner", "account.move", "account.move.line", "ir.attachment"]


class Contract(Model):
    model_config = ConfigDict(frozen=True)


class Scope(Contract):
    tenant_id: OpaqueId
    gestoria_company_id: LocalId


class PublicConnection(Contract):
    """Projection safe to serialize after checking authorization for its scope."""

    schema_version: SchemaVersion = 1
    connection_id: LocalId
    scope: Scope
    provider: Literal["odoo_community"] = "odoo_community"
    provider_version: Literal["19.0"] = "19.0"
    state: Literal["pending_validation", "active", "disabled"]
    created_at: Timestamp
    revision: Revision


class OdooBinding(Contract):
    """Server-side references only. Keep this object out of public projections."""

    scope: Scope
    connection_id: LocalId
    endpoint_ref: OpaqueId
    database_ref: OpaqueId
    credential_ref: OpaqueId
    odoo_company_id: RemoteId


class CapabilityReport(Contract):
    schema_version: SchemaVersion = 1
    connection_id: LocalId
    checked_at: Timestamp
    contacts_read: Literal["supported", "unsupported", "denied", "unknown"]
    invoices_read: Literal["supported", "unsupported", "denied", "unknown"]


class SyncCursor(Contract):
    """Keyset cursor for server-side paging in a single connection and model."""

    connection_id: LocalId
    model: RemoteModel
    write_date: Timestamp
    remote_id: RemoteId


class SourceRef(Contract):
    connection_id: LocalId
    model: RemoteModel
    remote_id: RemoteId
    remote_write_date: Timestamp | None = None
    observed_at: Timestamp
    content_hash: Digest
    mapping_version: OpaqueId


class ExternalObjectLink(Contract):
    scope: Scope
    source: SourceRef
    local_kind: Literal["contact", "economic_record", "document"]
    local_id: LocalId
    sync_status: Literal["current", "conflict", "missing"]


class Money(Contract):
    """Decimal strings are part of the wire contract, including for zero."""

    amount: Annotated[str, Field(strict=True, pattern=r"^-?(0|[1-9][0-9]{0,14})(\.[0-9]{1,6})?$")]
    currency: Annotated[str, Field(strict=True, pattern=r"^[A-Z]{3}$")]


class InvoiceSourceRef(SourceRef):
    model: Literal["account.move"]


class ImportedEconomicFact(Contract):
    """ERP staging evidence. Fiscal treatment and eligibility remain unresolved."""

    schema_version: SchemaVersion = 1
    scope: Scope
    source: InvoiceSourceRef
    erp_state: Literal["draft", "posted", "cancel"]
    gross_total: Money
    review_status: Literal["unverified"] = "unverified"


class ReadRequest(Contract):
    """Validated parameters only. The server must supply the scope separately."""

    limit: PageSize = 100


class ContactRead(ReadRequest):
    capability: Literal["contacts.read"]


class InvoiceRead(ReadRequest):
    capability: Literal["invoices.read"]


ReadCommand = Annotated[ContactRead | InvoiceRead, Field(discriminator="capability")]


class OperationEnvelope(Contract):
    """Trusted server envelope assembled after authenticating the caller."""

    schema_version: SchemaVersion = 1
    scope: Scope
    actor_id: OpaqueId
    correlation_id: OpaqueId
    causation_id: OpaqueId | None = None
    command: ReadCommand


class ResultBase(Contract):
    schema_version: SchemaVersion = 1
    correlation_id: OpaqueId


class ReadSucceeded(ResultBase):
    status: Literal["succeeded"]
    records: Annotated[tuple[SourceRef, ...], Field(max_length=200)]
    next_cursor: SyncCursor | None = None


class ReadUnavailable(ResultBase):
    status: Literal["unavailable"]
    reason: Literal["unsupported", "denied", "not_configured"]


class ReadFailed(ResultBase):
    status: Literal["failed"]
    reason: Literal["timeout", "provider_unavailable", "invalid_response", "invalid_cursor"]
    retryable: Annotated[bool, Field(strict=True)]


ReadResult = Annotated[ReadSucceeded | ReadUnavailable | ReadFailed, Field(discriminator="status")]
READ_RESULT = TypeAdapter(ReadResult)
