import json

from agntia_gestoria.auth import Actor
from agntia_gestoria.integrations.security.__main__ import main
from agntia_gestoria.integrations.security.agent import SecurityAgent
from agntia_gestoria.integrations.security.notifier import MemoryChannel, Notifier
from agntia_gestoria.integrations.security.watcher import Watcher
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
TRAVERSAL = '/api/' + '..' + '/..' + '/sistema'


def agent_with(notify=False):
    watcher = Watcher()
    channel = MemoryChannel()
    agent = SecurityAgent(watcher, Notifier(channel, min_seconds=0))
    return agent, watcher, channel


def test_repeated_denials_are_grouped_by_actor():
    agent, watcher, _ = agent_with()
    for _ in range(3):
        watcher.observe('GET', '/api/x', 401, 2, actor='luis-rev')
    watcher.observe('GET', '/api/y', 401, 2, actor='otra')
    patterns = agent.anomalies()
    assert [item['code'] for item in patterns] == ['auth_burst']
    assert patterns[0]['actor'] == 'luis-rev' and patterns[0]['count'] == 3


def test_repeated_server_errors_and_critical_paths_are_reported():
    agent, watcher, _ = agent_with()
    watcher.observe('GET', '/api/x', 500, 900)
    watcher.observe('GET', '/api/y', 500, 800)
    watcher.observe('GET', TRAVERSAL, 404, 3)
    codes = [item['code'] for item in agent.anomalies()]
    assert 'server_errors' in codes
    assert 'critical_path' in codes


def test_single_denial_is_not_an_anomaly():
    agent, watcher, _ = agent_with()
    watcher.observe('GET', '/api/x', 401, 2, actor='luis-rev')
    assert agent.anomalies() == []


def test_digest_mentions_patterns_and_raises_severity():
    agent, watcher, channel = agent_with()
    for _ in range(3):
        watcher.observe('GET', '/api/x', 403, 2, actor='luis-rev')
    report = agent.digest(notify=True)
    assert 'Patrones:' in report['summary']
    assert report['anomalies']
    assert channel.last()['severity'] == 'high'
    assert 'accesos denegados' in channel.last()['text']


def test_chat_returns_what_was_sent():
    agent, watcher, _ = agent_with()
    watcher.observe('GET', '/api/x', 500, 10)
    assert agent.chat()['messages'] == []
    agent.digest(notify=True)
    history = agent.chat()
    assert history['available'] is True
    assert 'Seguridad' in history['messages'][0]['text']


def seed(tmp_path):
    database = Database(str(tmp_path))
    with database.transaction() as connection:
        connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                           (CID, canonical({'id': CID, 'name': 'Uno'})))
        Database.audit(connection, CID, Actor('ana', 'owner', ('*',)),
                       'rrhh.closure.prepare', 'obj-1', {'period': '2026-10'})
    return database


def test_cli_reports_a_valid_chain(tmp_path, capsys):
    seed(tmp_path)
    assert main(['--db', str(tmp_path), '--company', CID]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report['valid'] is True
    assert report['events'] == 1


def test_cli_rejects_an_invalid_company(tmp_path):
    assert main(['--db', str(tmp_path), '--company', 'no-es-hex32']) == 2


def test_cli_flags_a_broken_chain(tmp_path, capsys):
    database = seed(tmp_path)
    with database.transaction() as connection:
        row = connection.execute('SELECT seq,body FROM audit WHERE company_id=?', (CID,)).fetchone()
        tampered = json.loads(row['body'])
        tampered['actor_id'] = 'otra-persona'
        connection.execute('UPDATE audit SET body=? WHERE seq=?',
                           (canonical(tampered), row['seq']))
    assert main(['--db', str(tmp_path), '--company', CID]) == 1
    assert json.loads(capsys.readouterr().out)['valid'] is False
