"""Configuración RRHH por empresa, siempre resuelta en servidor.

`GESTORIA_RRHH_JSON` es un objeto `{company_id: {...}}`. Una empresa sin
`enabled: true` no expone ninguna capacidad: se responde 404 con código del
contrato, nunca un error genérico ni una lista vacía que parezca funcionar.
"""
import json
import os
from dataclasses import dataclass

from ..errors import reject


@dataclass(frozen=True)
class RrhhConfig:
    company_id: str
    timezone: str
    policy_version: str
    payroll_provider: str | None = None


def raw_config():
    value = os.getenv('GESTORIA_RRHH_JSON', '{}')
    try:
        data = json.loads(value)
    except ValueError as exc:
        raise ValueError('GESTORIA_RRHH_JSON no es JSON válido') from exc
    if not isinstance(data, dict):
        raise ValueError('GESTORIA_RRHH_JSON debe ser un objeto por empresa')
    for company_id, item in data.items():
        if not isinstance(company_id, str) or not isinstance(item, dict):
            raise ValueError('GESTORIA_RRHH_JSON contiene una entrada inválida')
    return data


def config_for(company_id, *, raw=None):
    data = raw_config() if raw is None else raw
    item = data.get(company_id)
    if not isinstance(item, dict) or item.get('enabled') is not True:
        reject('capability_not_available', 'RR. HH. no está habilitado para esta empresa', 404)
    timezone = item.get('timezone')
    policy_version = item.get('policy_version')
    if not isinstance(timezone, str) or not timezone:
        reject('configuration', 'Falta la zona horaria de RR. HH.', 400)
    if not isinstance(policy_version, str) or not policy_version:
        reject('configuration', 'Falta la versión de política de RR. HH.', 400)
    provider = item.get('payroll_provider')
    if provider is not None and not isinstance(provider, str):
        reject('configuration', 'payroll_provider debe ser texto o nulo', 400)
    return RrhhConfig(company_id, timezone, policy_version, provider)
