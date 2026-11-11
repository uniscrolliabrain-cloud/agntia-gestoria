from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated,Literal

from pydantic import Field,StrictStr,field_validator
from ..models import Model

HexId=Annotated[str,Field(pattern=r'^[a-f0-9]{32}$')]
Opaque=Annotated[str,Field(min_length=1,max_length=160,pattern=r'^[a-zA-Z0-9_.:@/-]+$')]


class Money(Model):
    currency:Literal['EUR']='EUR'
    amount:Decimal=Field(max_digits=18,decimal_places=2)
    @field_validator('amount',mode='before')
    @classmethod
    def decimal_input(cls,value):
        if not isinstance(value,(str,Decimal)):raise ValueError('Money requires a decimal string')
        return value


class ConnectionCreate(Model):
    server_ref:Opaque


class BindingValidation(Model):
    revision:int=Field(ge=0)
    confirm_fiscal_identity:bool=False
    notes:str=Field(default='',max_length=3000)


class Revision(Model):
    revision:int=Field(ge=0)


class CapabilityReport(Model):
    schema_version:Literal[1]=1
    provider_version:str
    checked_at:datetime
    supported:dict[str,bool]
    unsupported:list[str]=Field(default_factory=list)
    evidence_hash:str


class OdooConnectionPublic(Model):
    connection_id:HexId
    gestoria_company_id:HexId
    tenant_id:Opaque
    provider:Literal['odoo_community']='odoo_community'
    provider_version:Literal['19.0']='19.0'
    state:Literal['pending_validation','ready','degraded','disabled']
    revision:int
    capabilities:list[str]


class ExternalObjectLink(Model):
    id:HexId
    gestoria_company_id:HexId
    connection_id:HexId
    provider:Literal['odoo_community']='odoo_community'
    model:Literal['res.partner','account.move','account.move.line','ir.attachment']
    external_id:str=Field(min_length=1,max_length=160)
    local_kind:str
    local_id:HexId
    remote_write_date:str|None=None
    source_hash:str=Field(pattern=r'^[a-f0-9]{64}$')
    mapping_version:Literal['odoo19-v1']='odoo19-v1'
    last_seen_at:datetime
    sync_status:Literal['linked','conflict','missing','detached']='linked'


class ImportPreview(Model):
    schema_version:Literal[1]=1
    id:HexId
    mapping_version:Literal['odoo19-v1']='odoo19-v1'
    state:Literal['staged','mapping_blocked','imported','conflict']
    source_hash:str
    warnings:list[str]


class SyncCursor(Model):
    write_date:str|None=None
    external_id:int=Field(default=0,ge=0)
    overlap_seconds:int=Field(default=5,ge=0,le=300)


class SyncJob(Model):
    id:HexId
    company_id:HexId
    connection_id:HexId
    state:Literal['pending','running','succeeded','failed','reconciliation_required','blocked']
    attempts:int=Field(ge=0)
    revision:int=Field(ge=0)
    correlation_id:str


class Conflict(Model):
    id:HexId
    company_id:HexId
    connection_id:HexId
    reason:Literal['remote_changed','remote_missing','remote_cancelled','mapping_blocked','write_uncertain']
    state:Literal['open','resolved']


class EvidenceRef(Model):
    id:HexId
    sha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    source_system:Literal['odoo_community']='odoo_community'
    external_object_id:str


class ImportRequest(Model):
    staging_ids:list[HexId]=Field(min_length=1,max_length=200)
    idempotency_key:Opaque


class PreviewRequest(Model):
    resource:Literal['partners','invoices']='invoices'
    full:bool=False


class ApprovalRequest(Model):
    revision:int=Field(ge=0)
    proposal_hash:str=Field(pattern=r'^[a-f0-9]{64}$')
    notes:str=Field(min_length=5,max_length=3000)


class CommitRequest(Model):
    proposal_id:HexId
    approval_id:HexId
    expected_revision:int=Field(ge=0)
    idempotency_key:Opaque


class PartnerChange(Model):
    name:str=Field(min_length=2,max_length=160)
    email:str=Field(default='',max_length=254)
    vat:str=Field(default='',max_length=40)
    is_company:bool=False
    remote_id:int|None=Field(default=None,gt=0)
    expected_remote_write_date:str|None=None
    @field_validator('email')
    @classmethod
    def email_valid(cls,value):
        if value and ('@' not in value or any(c in value for c in '\r\n')):raise ValueError('Invalid email')
        return value


class DraftInvoiceRequest(Model):
    invoice_draft_id:HexId
    partner_id:int=Field(gt=0)
    journal_id:int=Field(gt=0)
    account_id:int=Field(gt=0)
    tax_ids:list[int]=Field(default_factory=list,max_length=10)
    expected_draft_hash:str=Field(pattern=r'^[a-f0-9]{64}$')
    @field_validator('tax_ids')
    @classmethod
    def positive_ids(cls,value):
        if len(set(value))!=len(value) or any(type(v)!=int or v<=0 for v in value):raise ValueError('Invalid tax identifiers')
        return value


class OperationEnvelope(Model):
    schema_version:Literal[1]=1
    tenant_id:Opaque
    company_id:HexId
    actor_id:Opaque
    capability:Literal['partners.propose','invoices.propose','writes.commit','imports.run']
    correlation_id:str
    causation_id:str|None=None
    idempotency_key:Opaque
    approval_id:HexId|None=None
    expected_revision:int=Field(ge=0)
    dry_run:bool=True
    payload:dict


class OperationResult(Model):
    status:Literal['proposed','succeeded','reconciliation_required','blocked']
    local_id:HexId|None=None
    remote_id:int|None=None
    warnings:list[str]=Field(default_factory=list)
    evidence:list[EvidenceRef]=Field(default_factory=list)
    source_hash:str|None=None
    mapping_version:Literal['odoo19-v1']='odoo19-v1'
    retryable:bool=False
    reconciliation_required:bool=False
