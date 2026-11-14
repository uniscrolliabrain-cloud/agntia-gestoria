import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agntia_gestoria.integrations.security.middleware import SecurityMiddleware
from agntia_gestoria.integrations.security.notifier import MemoryChannel, Notifier
from agntia_gestoria.integrations.security.watcher import Watcher, classify, redact


def test_redaction_never_keeps_credential_values():
    headers = {'Authorization': 'Bearer secretisimo', 'Cookie': 'session=abc',
               'User-Agent': 'curl/8', 'X-Trace': 'abc'}
    result = redact(headers)
    assert result['authorization'] == '<redactado>'
    assert result['cookie'] == '<redactado>'
    assert 'secretisimo' not in json.dumps(result)
    assert result['user-agent'] == 'curl/8'
    assert result['x-trace'] == '<oculto>'


def test_severity_is_explained_by_reason():
    assert classify('GET', '/api/x', 200) == ('ok', 'info', 'Petición atendida')
    assert classify('GET', '/api/x', 401)[0] == 'auth_denied'
    assert classify('GET', '/api/x', 500)[1] == 'high'
    traversal = '/api/' + '..' + '/..' + '/sistema'
    assert classify('GET', traversal, 404)[1] == 'critical'
    assert classify('POST', '/api/companies/a/rrhh/closures', 200)[0] == 'rrhh_write'


def test_watcher_keeps_a_bounded_window_and_counts():
    watcher = Watcher(size=3)
    for index in range(5):
        watcher.observe('GET', f'/api/{index}', 200, 5)
    counts = watcher.counts()
    assert counts['total'] == 3
    assert counts['severity'] == {'info': 3}
    assert len(watcher.events()) == 3


def test_middleware_sees_success_and_failure():
    watcher = Watcher()
    app = FastAPI()
    app.add_middleware(SecurityMiddleware, watcher=watcher)

    @app.get('/ok')
    def ok():
        return {'ok': True}

    @app.get('/boom')
    def boom():
        raise RuntimeError('fallo de prueba')

    with TestClient(app, raise_server_exceptions=False) as client:
        client.get('/ok')
        client.get('/boom')

    codes = [event['code'] for event in watcher.events()]
    assert codes == ['server_error', 'ok']
    assert watcher.events()[0]['status'] == 500


def test_notifier_throttles_bursts():
    clock = {'now': 1000.0}
    channel = MemoryChannel()
    notifier = Notifier(channel, min_seconds=60, clock=lambda: clock['now'])
    assert notifier.send('uno')['reason'] == 'sent'
    assert notifier.send('dos')['reason'] == 'throttled'
    clock['now'] += 61
    assert notifier.send('tres')['reason'] == 'sent'
    assert [message['text'] for message in channel.messages] == ['uno', 'tres']
