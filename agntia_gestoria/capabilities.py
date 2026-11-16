"""Manifiesto de capacidades v1 (campaña C01).

Fuente única para saber qué puede hacer el middleware, con qué rol, si muta
estado y si exige intervención humana. Se deriva de la política real
(`integrations/policy.py`) y se valida contra las rutas que el servicio expone,
de modo que el manifiesto no puede declarar una capacidad inexistente ni una
lectura que escribe.
"""

import json
import sys
from pathlib import Path

from .integrations import policy

VERSION = 1

READ_ROLES = ("owner", "reviewer", "agent", "viewer")
PROPOSE_ROLES = ("owner", "reviewer", "agent")
HUMAN_ROLES = ("owner", "reviewer")

# Rutas HTTP que exponen cada capacidad. Las que se resuelven dentro del
# adaptador (por ejemplo `contacts.read` al previsualizar un contacto) se
# declaran con lista vacía y `exposed_through: "internal"`.
CAPABILITIES = (
    {"id": "health", "provider": "odoo", "http": [("GET", "/api/companies/{cid}/integrations/odoo/health")]},
    {"id": "contacts.read", "provider": "odoo", "http": []},
    {"id": "invoices.read", "provider": "odoo", "http": [("GET", "/api/companies/{cid}/integrations/odoo/invoices/{invoice_id}/attachments")]},
    {"id": "jobs.read", "provider": "odoo", "http": [("GET", "/api/companies/{cid}/integrations/odoo/jobs/{job_id}")]},
    {"id": "conflicts.read", "provider": "odoo", "http": [("GET", "/api/companies/{cid}/integrations/odoo/conflicts")]},
    {"id": "events.read", "provider": "odoo", "http": [("GET", "/api/companies/{cid}/integrations/odoo/events")]},
    {"id": "metrics.read", "provider": "odoo", "http": [("GET", "/api/companies/{cid}/integrations/odoo/metrics")]},
    {"id": "events.ack", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/events/ack")]},
    {"id": "imports.run", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/imports"), ("POST", "/api/companies/{cid}/integrations/odoo/imports/preview")]},
    {"id": "partners.propose", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/partners/dry-run")]},
    {"id": "invoices.propose", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/invoice-drafts/dry-run")]},
    {"id": "connections.manage", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/connections"), ("POST", "/api/companies/{cid}/integrations/odoo/connections/validate"), ("POST", "/api/companies/{cid}/integrations/odoo/connections/disable")]},
    {"id": "approvals.create", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/proposals/{proposal_id}/approve")]},
    {"id": "writes.commit", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/partners/commit"), ("POST", "/api/companies/{cid}/integrations/odoo/invoice-drafts/commit"), ("POST", "/api/companies/{cid}/integrations/odoo/writes/reconcile")]},
    {"id": "conflicts.resolve", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/conflicts/{conflict_id}/resolve")]},
    {"id": "records.classify", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/records/{record_id}/classification")]},
    {"id": "attachments.download", "provider": "odoo", "http": [("POST", "/api/companies/{cid}/integrations/odoo/invoices/{invoice_id}/attachments/download")]},
)


def _kind(capability):
    if capability in policy.READ:
        return "read"
    if capability in policy.PROPOSE:
        return "propose"
    if capability in policy.HUMAN:
        return "human"
    raise KeyError(capability)


def _roles(kind):
    return {"read": READ_ROLES, "propose": PROPOSE_ROLES, "human": HUMAN_ROLES}[kind]


def manifest(commit=None):
    declared = {item["id"]: item for item in CAPABILITIES}
    unknown = sorted(set(policy.ALL) - set(declared))
    extra = sorted(set(declared) - set(policy.ALL))
    if unknown or extra:
        raise ValueError(f"Manifiesto desalineado con la política: faltan={unknown} sobran={extra}")
    capabilities = []
    for capability in sorted(policy.ALL):
        item = declared[capability]
        kind = _kind(capability)
        capabilities.append(
            {
                "id": capability,
                "kind": kind,
                "mutates": kind != "read",
                "roles": list(_roles(kind)),
                "provider": item["provider"],
                "human_approval_required": kind == "human",
                "exposed_through": "http" if item["http"] else "internal",
                "http": [{"method": method, "path": path} for method, path in item["http"]],
            }
        )
    return {
        "schema_version": VERSION,
        "generated_from": {"commit": commit} if commit else {},
        "capabilities": capabilities,
        "totals": {
            "capabilities": len(capabilities),
            "read": sum(1 for c in capabilities if c["kind"] == "read"),
            "propose": sum(1 for c in capabilities if c["kind"] == "propose"),
            "human": sum(1 for c in capabilities if c["kind"] == "human"),
        },
        "notice": (
            "Manifiesto de capacidades del middleware Gestoría. Declara lo que el servicio "
            "puede ejecutar y con qué rol; no acredita habilitación por empresa ni verificación "
            "contra un Odoo real."
        ),
    }


def route_index(app):
    """Rutas reales del servicio, tal y como las resuelve FastAPI."""
    index = {}
    for path, operations in app.openapi().get("paths", {}).items():
        index[path] = {method.upper() for method in operations}
    return index


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[1]
    commit = None
    git_head = root / ".git" / "HEAD"
    if git_head.exists():
        commit = _read_commit(root)
    json.dump(manifest(commit), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _read_commit(root):
    import subprocess

    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    return result.stdout.strip() or None


if __name__ == "__main__":
    main()
