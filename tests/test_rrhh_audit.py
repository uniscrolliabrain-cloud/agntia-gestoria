import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agntia_gestoria.integrations.rrhh import snapshot
from agntia_gestoria.integrations.rrhh.audit import trail
from agntia_gestoria.integrations.rrhh.routes import register_rrhh_routes
from agntia_gestoria.integrations.rrhh.routes_audit import register_audit_routes
from agntia_gestoria.integrations.rrhh.routes_closure import register_closure_routes
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
OWNER = 'owner-token-1234567890'
REVIEWER = 'reviewer-token-1234567890'
VIEWER = 'viewer-token-1234567890'
PACKS = Path(__file__).parent / 'fixtures' / 'rrhh' / 'packs'
PUNCHES = [{'at': '2026-10-05T08:00:00+02:00', 'direction': 'in'},
           {'at': '2026-10-05T16:00:00+02:00', 'direction': 'out'}]


def setup(tmp_path, monkeypatch):
    monkeypatch.setenv('GESTORIA_OWNER_TOKEN', OWNER)
    monkeypatch.setenv('GESTORIA_ACTORS_JSON', json.dumps({
        REVIEWER: {'id': 'luis-rev', 'role': 'reviewer', 'companies': [CID]},
        VIEWER: {'id': 'vero-view', 'role': 'viewer', 'companies': [CID]},
    }))
    monkeypatch.setenv('GESTORIA_RRHH_JSON', json.dumps({
        CID: {'enabled': True, 'timezone': 'Europe/Madrid', 'policy_version': '2026-11'}}))
    monkeypatch.setenv('GESTORIA_RRHH_SECTOR', 'hosteleria')
    monkeypatch.setenv('GESTORIA_RRHH_PACKS', str(PACKS))
    db = Database(str(tmp_path))
    with db.transaction() as connection:
        connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                           (CID, canonical({'id': CID, 'name': 'Uno'})))
        snapshot.persist_snapshot(
            connection, CID, '2026-10',
            lambda: {'marker': 'v1', 'sources': {'employees': [
                {'ref': 'e1', 'punches': PUNCHES, 'absences': []}]}},
            policy_hash='p' * 10, timezone='Europe/Madrid')
    app = FastAPI()
    register_rrhh_routes(app, db)
    register_closure_routes(app, db)
    register_audit_routes(app, db)
    return db, TestClient(app)


def auth(token):
    return {'Authorization': f'Bearer {token}'}


def full_flow(client):
    client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                json={'period': '2026-10'})
    client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/approve', headers=auth(REVIEWER),
                json={'justification': 'Revisados fichajes y pausas del mes'})
    client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/export', headers=auth(REVIEWER))


def test_every_state_change_leaves_a_linked_event(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    with http as client:
        full_flow(client)
        response = client.get(f'/api/companies/{CID}/rrhh/audit', headers=auth(OWNER))
    body = response.json()
    assert response.status_code == 200
    assert body['valid'] is True
    assert body['events'] == 3
    assert body['actions'] == ['rrhh.closure.prepare', 'rrhh.closure.approve',
                               'rrhh.closure.export']


def test_repeating_an_idempotent_call_adds_no_events(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    with http as client:
        full_flow(client)
        client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                    json={'period': '2026-10'})
        client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/export',
                    headers=auth(REVIEWER))
        body = client.get(f'/api/companies/{CID}/rrhh/audit', headers=auth(OWNER)).json()
    assert body['events'] == 3


def test_a_rewritten_event_breaks_the_chain(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    with http as client:
        full_flow(client)
    with db.transaction() as connection:
        row = connection.execute('SELECT seq,body FROM audit WHERE company_id=? ORDER BY seq',
                                 (CID,)).fetchall()[1]
        tampered = json.loads(row['body'])
        tampered['actor_id'] = 'otra-persona'
        connection.execute('UPDATE audit SET body=? WHERE seq=?', (canonical(tampered), row['seq']))
        report = trail(connection, CID)
    assert report['valid'] is False
    assert report['broken_at'] == 2


def test_a_viewer_cannot_read_the_trail(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    with http as client:
        response = client.get(f'/api/companies/{CID}/rrhh/audit', headers=auth(VIEWER))
    assert response.status_code == 403


def test_the_trail_never_contains_punch_times(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    with http as client:
        full_flow(client)
        text = client.get(f'/api/companies/{CID}/rrhh/audit', headers=auth(OWNER)).text
    assert '08:00' not in text
    assert '2026-10-05T' not in text
