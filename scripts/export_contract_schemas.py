#!/usr/bin/env python3
"""Escribe los esquemas versionados consumidos desde el que fuera el cliente.

Uso: python scripts/export_contract_schemas.py [ruta]
Por defecto escribe docs/odoo-adapter/schemas/contracts-v1.json. El test de
contratos compara el fichero versionado con la exportación actual para detectar
deriva de esquema.
"""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from agntia_gestoria.integrations.contracts_export import export  # noqa: E402


def main(path=None):
    target=Path(path) if path else ROOT/'docs/odoo-adapter/schemas/contracts-v1.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(export(),ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    return target


if __name__=='__main__':
    print(main(sys.argv[1] if len(sys.argv)>1 else None))
