import json
import unittest

from pydantic import ValidationError

from agntia_gestoria.integrations.contracts import (
    ImportedEconomicFact,
    Money,
    OdooBinding,
    OperationEnvelope,
    PublicConnection,
    READ_RESULT,
    SourceRef,
    SyncCursor,
)


LOCAL = "a" * 32
SCOPE = {"tenant_id": "tenant-demo", "gestoria_company_id": LOCAL}
NOW = "2026-11-10T12:30:00Z"
SOURCE = {
    "connection_id": LOCAL,
    "model": "account.move",
    "remote_id": 12,
    "remote_write_date": NOW,
    "observed_at": NOW,
    "content_hash": "sha256:" + "0" * 64,
    "mapping_version": "v1",
}


class IntegrationContractsTests(unittest.TestCase):
    def test_public_connection_has_no_credential_references(self):
        binding = OdooBinding(
            scope=SCOPE, connection_id=LOCAL, endpoint_ref="endpoint-a", database_ref="db-a",
            credential_ref="secret-a", odoo_company_id=3,
        )
        public = PublicConnection(
            scope=binding.scope, connection_id=binding.connection_id,
            state="pending_validation", created_at=NOW, revision=0,
        )
        wire = public.model_dump_json()
        self.assertNotIn("secret-a", wire)
        self.assertNotIn("credential_ref", PublicConnection.model_json_schema()["properties"])
        self.assertEqual(PublicConnection.model_validate_json(wire), public)
        with self.assertRaises(ValidationError):
            PublicConnection.model_validate({**public.model_dump(), "credential_ref": "secret-a"})

    def test_strict_identifiers_timestamps_and_hash(self):
        self.assertEqual(SourceRef.model_validate(SOURCE).model_dump(mode="json")["observed_at"], NOW)
        for field, invalid in [
            ("connection_id", "Company A"),
            ("remote_id", True),
            ("remote_id", "12"),
            ("remote_id", 0),
            ("observed_at", 1_794_315_600),
            ("observed_at", "2026-11-10T12:30:00"),
            ("observed_at", "2026-11-10 12:30:00Z"),
            ("content_hash", "sha256:secret"),
            ("model", "arbitrary.model"),
        ]:
            with self.subTest(field=field, invalid=invalid), self.assertRaises(ValidationError):
                SourceRef.model_validate({**SOURCE, field: invalid})
        with self.assertRaises(ValidationError):
            SyncCursor(connection_id=LOCAL, model="res.partner", write_date=NOW, remote_id=False)

    def test_economic_fact_retains_decimal_string_and_unverified_status(self):
        fixture = {
            "scope": SCOPE, "source": SOURCE, "erp_state": "draft",
            "gross_total": {"amount": "100.10", "currency": "EUR"},
        }
        fact = ImportedEconomicFact.model_validate_json(json.dumps(fixture))
        self.assertEqual(fact.review_status, "unverified")
        self.assertEqual(fact.model_dump(mode="json")["gross_total"]["amount"], "100.10")
        with self.assertRaises(ValidationError):
            ImportedEconomicFact.model_validate({**fixture, "review_status": "reviewed"})
        with self.assertRaises(ValidationError):
            ImportedEconomicFact.model_validate({**fixture, "source": {**SOURCE, "model": "res.partner"}})
        for amount in ("NaN", "Infinity", "1e5", "00.50", "1.0000001", 1.1, 1, True):
            with self.subTest(amount=amount), self.assertRaises(ValidationError):
                Money(amount=amount, currency="EUR")

    def test_command_has_no_arbitrary_remote_parameters(self):
        fixture = {"scope": SCOPE, "actor_id": "agent-a", "correlation_id": "req-1"}
        envelope = OperationEnvelope.model_validate({**fixture, "command": {"capability": "contacts.read"}})
        self.assertEqual(envelope.command.limit, 100)
        self.assertEqual(OperationEnvelope.model_validate_json(envelope.model_dump_json()), envelope)
        for command in [
            {"capability": "contacts.write"},
            {"capability": "contacts.read", "limit": 201},
            {"capability": "contacts.read", "limit": "2"},
            {"capability": "contacts.read", "scope": SCOPE},
            {"capability": "contacts.read", "context": {"allowed_company_ids": [2]}},
            {"capability": "invoices.read", "method": "action_post"},
        ]:
            with self.subTest(command=command), self.assertRaises(ValidationError):
                OperationEnvelope.model_validate({**fixture, "command": command})

    def test_discriminated_results_and_schema(self):
        values = [
            {"status": "succeeded", "records": [SOURCE]},
            {"status": "unavailable", "reason": "denied"},
            {"status": "failed", "reason": "timeout", "retryable": True},
        ]
        for item in values:
            parsed = READ_RESULT.validate_python({"correlation_id": "req-1", **item})
            self.assertEqual(READ_RESULT.validate_json(READ_RESULT.dump_json(parsed)), parsed)
        schema = READ_RESULT.json_schema()
        self.assertEqual(set(schema["discriminator"]["mapping"]), {"succeeded", "unavailable", "failed"})
        with self.assertRaises(ValidationError):
            READ_RESULT.validate_python({"correlation_id": "req-1", "status": "failed", "reason": "timeout"})
        for version in (True, 1.0, "1", 2):
            with self.subTest(version=version), self.assertRaises(ValidationError):
                READ_RESULT.validate_python({"schema_version": version, "correlation_id": "req-1", **values[0]})
        with self.assertRaises(ValidationError):
            READ_RESULT.validate_python({
                "correlation_id": "req-1", "status": "unavailable", "reason": "denied", "detail": "raw traceback",
            })
