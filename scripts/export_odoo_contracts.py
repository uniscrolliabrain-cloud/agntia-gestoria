"""Export the versioned wire contracts without importing the service or its DB."""

import json

from agntia_gestoria.integrations.contracts import (
    CONTACT_WRITE_RESULT,
    CapabilityReport,
    ContactPreviewRequest,
    ImportedEconomicFact,
    OperationEnvelope,
    PublicConnection,
    READ_RESULT,
)


def main():
    contracts = (PublicConnection, CapabilityReport, ImportedEconomicFact, OperationEnvelope, ContactPreviewRequest)
    schemas = {contract.__name__: contract.model_json_schema() for contract in contracts}
    schemas["ReadResult"] = READ_RESULT.json_schema()
    schemas["ContactWriteResult"] = CONTACT_WRITE_RESULT.json_schema()
    print(json.dumps(schemas, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
