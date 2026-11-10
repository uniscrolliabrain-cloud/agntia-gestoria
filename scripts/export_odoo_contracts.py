"""Export the versioned wire contracts without importing the service or its DB."""

import json

from agntia_gestoria.integrations.contracts import (
    CapabilityReport,
    ImportedEconomicFact,
    OperationEnvelope,
    PublicConnection,
    READ_RESULT,
)


def main():
    contracts = (PublicConnection, CapabilityReport, ImportedEconomicFact, OperationEnvelope)
    schemas = {contract.__name__: contract.model_json_schema() for contract in contracts}
    schemas["ReadResult"] = READ_RESULT.json_schema()
    print(json.dumps(schemas, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
