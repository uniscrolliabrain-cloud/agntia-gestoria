from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Facts(Model):
    fiscal_year_end: date | None = None
    accounts_approved_on: date | None = None
    has_employees: bool | None = None
    processes_personal_data: bool | None = None
    corporate_taxpayer: bool | None = None
    vat_status: Literal["liable", "exempt", "unknown"] = "unknown"
    vat_periodicity: Literal["quarterly", "monthly", "unknown"] = "unknown"
    vat_return_required: bool | None = None
    irpf_payment_model: Literal["130", "131", "none", "unknown"] = "unknown"
    withholds_payroll: bool | None = None
    withholds_professionals: bool | None = None
    withholds_rent: bool | None = None
    reta_required: bool | None = None
    uses_sii: bool | None = None
    sif_in_scope: bool | None = None
    b2b_einvoice_in_scope: bool | None = None
    previous_year_turnover_over_8m: bool | None = None

    @model_validator(mode="after")
    def dates(self):
        if self.accounts_approved_on and (not self.fiscal_year_end or self.accounts_approved_on < self.fiscal_year_end):
            raise ValueError("La aprobación necesita un cierre anterior o igual")
        return self


Territory = Literal["common", "canarias", "araba", "bizkaia", "gipuzkoa", "navarra", "ceuta", "melilla"]
Administration = Literal["aeat", "atc", "araba", "bizkaia", "gipuzkoa", "navarra", "ceuta", "melilla"]


class TaxAdministrations(Model):
    corporate_tax: list[Administration] = Field(default_factory=list, max_length=8)
    irpf: list[Administration] = Field(default_factory=list, max_length=8)
    iva: list[Administration] = Field(default_factory=list, max_length=8)
    igic: list[Administration] = Field(default_factory=list, max_length=8)
    ipsi: list[Administration] = Field(default_factory=list, max_length=8)
    withholdings: list[Administration] = Field(default_factory=list, max_length=8)


class CompanyCreate(Model):
    name: str = Field(min_length=2, max_length=160)
    legal_form: Literal["autonomo", "sl"]
    tax_territory: Literal["common", "canarias", "foral", "araba", "bizkaia", "gipuzkoa", "navarra", "ceuta", "melilla", "unknown"] = "unknown"
    operation_territories: list[Territory] = Field(default_factory=list, max_length=8)
    tax_administrations: TaxAdministrations = Field(default_factory=TaxAdministrations)
    nif: str = Field(default="", max_length=32)
    address: str = Field(default="", max_length=500)
    activity: str = Field(default="", max_length=500)
    facts: Facts = Field(default_factory=Facts)


class CompanyEdit(CompanyCreate):
    revision: int = Field(ge=0)


Category = Literal["fiscal", "accounting", "corporate", "labour", "privacy", "other"]


class CaseCreate(Model):
    title: str = Field(min_length=2, max_length=200)
    category: Category = "other"
    description: str = Field(default="", max_length=20000)
    due_date: date | None = None
    source_ids: list[str] = Field(default_factory=list, max_length=30)
    document_ids: list[str] = Field(default_factory=list, max_length=100)


class CaseEdit(CaseCreate):
    revision: int = Field(ge=0)


class Revision(Model):
    revision: int = Field(ge=0)


class Review(Revision):
    decision: Literal["approve", "request_changes"]
    notes: str = Field(min_length=5, max_length=5000)
    verified_source_ids: list[str] = Field(default_factory=list, max_length=30)


class InvoiceLine(Model):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, le=1000000, decimal_places=6)
    unit_price: Decimal = Field(ge=0, le=100000000, decimal_places=6)
    tax_rate: Decimal = Field(ge=0, le=100, decimal_places=4)


class InvoiceDraft(Model):
    customer_name: str = Field(min_length=2, max_length=160)
    customer_nif: str = Field(default="", max_length=32)
    customer_address: str = Field(default="", max_length=500)
    operation_date: date
    tax_kind: Literal["iva", "igic", "ipsi", "other", "none"]
    withholding_rate: Decimal = Field(ge=0, le=100, decimal_places=4)
    lines: list[InvoiceLine] = Field(min_length=1, max_length=200)
    notes: str = Field(default="", max_length=5000)

    @model_validator(mode="after")
    def taxes(self):
        if self.tax_kind == "none" and any(line.tax_rate != 0 for line in self.lines):
            raise ValueError("Un borrador sin impuesto no puede contener cuotas")
        return self


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def invoice_totals(draft: InvoiceDraft):
    lines = []
    for line in draft.lines:
        base = money(line.quantity * line.unit_price)
        tax = money(base * line.tax_rate / 100)
        lines.append({**line.model_dump(mode="json"), "base": str(base), "tax": str(tax)})
    base = sum((Decimal(line["base"]) for line in lines), Decimal("0"))
    tax = sum((Decimal(line["tax"]) for line in lines), Decimal("0"))
    withholding = money(base * draft.withholding_rate / 100)
    return {"currency": "EUR", "rounding": "half_up_per_line", "lines": lines, "base": str(money(base)), "tax": str(money(tax)),
            "withholding": str(withholding), "total": str(money(base + tax - withholding))}


class JournalLine(Model):
    account: str = Field(min_length=1, max_length=32)
    description: str = Field(default="", max_length=500)
    debit: Decimal = Field(ge=0, le=1000000000000, decimal_places=2)
    credit: Decimal = Field(ge=0, le=1000000000000, decimal_places=2)

    @model_validator(mode="after")
    def one_side(self):
        if (self.debit > 0) == (self.credit > 0):
            raise ValueError("Cada línea debe tener debe o haber, no ambos ni ninguno")
        return self


class JournalDraft(Model):
    entry_date: date
    concept: str = Field(min_length=2, max_length=500)
    lines: list[JournalLine] = Field(min_length=2, max_length=200)
    document_ids: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def balanced(self):
        if sum(line.debit for line in self.lines) != sum(line.credit for line in self.lines):
            raise ValueError("El borrador de asiento debe cuadrar: debe = haber")
        return self
