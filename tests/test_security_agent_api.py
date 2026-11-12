import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agntia_gestoria.integrations.security.agent import SecurityAgent
from agntia_gestoria.integrations.security.notifier import MemoryChannel
from agntia_gestoria.integrations.security.routes_security import (
    build_agent, register_security_routes)
from agntia_gestoria.integrations.security.watcher import Watcher

OWNER = 'owner-token-1234567890'
VIEWER = 'viewer-token-1234567890'


def test_the_agent_only_reads_and_says_so():
    agent = SecurityAgent(Watcher())
    public = [name for name in dir(agent) if not name.startswith('_')]
    assert sorted(public) == ['digest', 'events', 'explain', 'mode', 'name', 'watchlist']
    assert agent.mode == 'read_only'
    assert 'bloquear peticiones' in agent.watchlist()['cannot']


def test_digest_summarises_without_leaking_credentials():
    watcher = Watcher()
    watcher.observe('GET', '/api/x', 401, 3, actor='luis-rev')
    watcher.observe('GET', '/api/y', 500, 900)
    agent = SecurityAgent(watcher)
    report = agent.digest()
    assert report['counts']['total'] == 2
    assert 'Seguridad · 2 peticiones' in report['summary']
    assert len(report['alerts']) == 1
    assert 'Solo lectura' in report['summary']
    assert 'luis-rev' in agent.explain(agent.events()[1])


def configure(monkeypatch):
    monkeypatch.setenv('GESTORIA_OWNER_TOKEN', OWNER)
    monkeypatch.setenv('GESTORIA_ACTORS_JSON', json.dumps({
        VIEWER: {'id': 'vero-view', 'role': 'viewer', 'companies': ['*']}}))
    monkeypatch.delenv('GESTORIA_SECURITY_CHAT_WEBHOOK', raising=False)


def test_routes_are_owner_only(monkeypatch):
    configure(monkeypatch)
    watcher = Watcher()
    watcher.observe('GET', '/api/x', 500, 10)
    app = FastAPI()
    register_security_routes(app, watcher)
    with TestClient(app) as client:
        assert client.get('/api/security/events',
                          headers={'Authorization': f'Bearer {VIEWER}'}).status_code == 403
        digest = client.get('/api/security/digest',
                            headers={'Authorization': f'Bearer {OWNER}'})
        watchlist = client.get('/api/security/watchlist',
                               headers={'Authorization': f'Bearer {OWNER}'})
    assert digest.status_code == 200
    assert digest.json()['mode'] == 'read_only'
    assert watchlist.json()['cannot']


def test_report_pushes_one_message_to_the_chat_channel(monkeypatch):
    configure(monkeypatch)
    watcher = Watcher()
    watcher.observe('GET', '/api/x', 401, 4)
    channel = MemoryChannel()
    agent = build_agent(watcher, channel)
    app = FastAPI()
    register_security_routes(app, watcher, agent)
    with TestClient(app) as client:
        response = client.post('/api/security/report',
                               headers={'Authorization': f'Bearer {OWNER}'})
    assert response.status_code == 200
    assert 'Seguridad · 1 peticiones' in channel.last()['text']
    assert channel.last()['severity'] == 'info'
