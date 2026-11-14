import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from agntia_gestoria.integrations.errors import IntegrationError
from agntia_gestoria.integrations.rrhh.config import config_for
from agntia_gestoria.integrations.rrhh.routes import register_rrhh_routes
from agntia_gestoria.storage import Database

CID = 'a' * 32
OTHER = 'b' * 32
OWNER = 'owner-token-1234567890'


def client(tmp_path, monkeypatch):
    monkeypatch.setenv('GESTORIA_OWNER_TOKEN', OWNER)
    app = FastAPI()
    register_rrhh_routes(app, Database(str(tmp_path)))
    return TestClient(app)


def enabled(monkeypatch, company=CID, **extra):
    monkeypatch.setenv('GESTORIA_RRHH_JSON', json.dumps({
        company: {'enabled': True, 'timezone': 'Europe/Madrid', 'policy_version': '2026-11', **extra}}))


def test_company_without_flag_is_not_available(monkeypatch):
    monkeypatch.delenv('GESTORIA_RRHH_JSON', raising=False)
    with pytest.raises(IntegrationError) as error:
        config_for(CID)
    assert error.value.code == 'capability_not_available'
    assert error.value.status == 404


def test_enabled_company_returns_config(monkeypatch):
    enabled(monkeypatch)
    config = config_for(CID)
    assert config.timezone == 'Europe/Madrid'
    assert config.policy_version == '2026-11'


def test_missing_timezone_is_a_configuration_error(monkeypatch):
    monkeypatch.setenv('GESTORIA_RRHH_JSON', json.dumps({CID: {'enabled': True}}))
    with pytest.raises(IntegrationError) as error:
        config_for(CID)
    assert error.value.code == 'configuration'


def test_malformed_json_is_rejected(monkeypatch):
    monkeypatch.setenv('GESTORIA_RRHH_JSON', '{no es json')
    with pytest.raises(ValueError):
        config_for(CID)


def test_capabilities_require_the_flag(tmp_path, monkeypatch):
    monkeypatch.delenv('GESTORIA_RRHH_JSON', raising=False)
    with client(tmp_path, monkeypatch) as http:
        response = http.get(f'/api/companies/{CID}/rrhh/capabilities',
                            headers={'Authorization': f'Bearer {OWNER}'})
    assert response.status_code == 404
    assert response.json()['detail']['code'] == 'capability_not_available'


def test_capabilities_list_contract_codes(tmp_path, monkeypatch):
    enabled(monkeypatch)
    with client(tmp_path, monkeypatch) as http:
        response = http.get(f'/api/companies/{CID}/rrhh/capabilities',
                            headers={'Authorization': f'Bearer {OWNER}'})
    assert response.status_code == 200
    body = response.json()
    assert body['enabled'] is True
    assert body['timezone'] == 'Europe/Madrid'
    assert 'rrhh.policy.read' in body['capabilities']


def test_health_is_scoped_to_the_company(tmp_path, monkeypatch):
    enabled(monkeypatch)
    with client(tmp_path, monkeypatch) as http:
        own = http.get(f'/api/companies/{CID}/rrhh/health', headers={'Authorization': f'Bearer {OWNER}'})
        other = http.get(f'/api/companies/{OTHER}/rrhh/health',
                         headers={'Authorization': f'Bearer {OWNER}'})
    assert own.status_code == 200
    assert own.json()['snapshot']['present'] is False
    assert other.status_code == 404


def test_health_never_exposes_configuration_secrets(tmp_path, monkeypatch):
    enabled(monkeypatch, payroll_provider='proveedor_prueba')
    with client(tmp_path, monkeypatch) as http:
        body = http.get(f'/api/companies/{CID}/rrhh/health',
                        headers={'Authorization': f'Bearer {OWNER}'}).text
    assert OWNER not in body
    assert 'proveedor_prueba' not in body
