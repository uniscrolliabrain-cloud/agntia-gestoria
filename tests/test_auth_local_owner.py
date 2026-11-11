import pytest
from fastapi import HTTPException
from starlette.requests import Request

from agntia_gestoria import auth


def request_from(host):
    return Request({'type': 'http', 'method': 'GET', 'path': '/', 'headers': [],
                    'client': (host, 5000), 'scheme': 'http', 'server': ('testserver', 80)})


def no_credentials(monkeypatch):
    monkeypatch.delenv('GESTORIA_OWNER_TOKEN', raising=False)
    monkeypatch.setenv('GESTORIA_ACTORS_JSON', '{}')


def test_loopback_is_not_owner_without_explicit_permission(monkeypatch):
    no_credentials(monkeypatch)
    monkeypatch.delenv('GESTORIA_ALLOW_LOCAL_OWNER', raising=False)
    with pytest.raises(HTTPException) as error:
        auth.authenticate(request_from('127.0.0.1'))
    assert error.value.status_code == 403


def test_loopback_is_owner_with_explicit_permission(monkeypatch):
    no_credentials(monkeypatch)
    monkeypatch.setenv('GESTORIA_ALLOW_LOCAL_OWNER', 'true')
    actor = auth.authenticate(request_from('127.0.0.1'))
    assert actor.role == 'owner' and actor.id == 'local-owner'


def test_remote_client_is_never_owner(monkeypatch):
    no_credentials(monkeypatch)
    monkeypatch.setenv('GESTORIA_ALLOW_LOCAL_OWNER', 'true')
    with pytest.raises(HTTPException):
        auth.authenticate(request_from('203.0.113.9'))


def test_testclient_keeps_working_for_the_suite(monkeypatch):
    no_credentials(monkeypatch)
    assert auth.authenticate(request_from('testclient')).id == 'local-owner'
