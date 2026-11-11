import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agntia_gestoria.integrations.rrhh import snapshot
from agntia_gestoria.integrations.rrhh.routes import register_rrhh_routes
from agntia_gestoria.integrations.rrhh.routes_closure import register_closure_routes
from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
OTHER = 'b' * 32
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
    app = FastAPI()
    register_rrhh_routes(app, db)
    register_closure_routes(app, db)
    return db, TestClient(app)


def seed(db, period='2026-10', employees=None, company=CID):
    sources = {'employees': employees if employees is not None else [
        {'ref': 'e1', 'punches': PUNCHES, 'absences': []}]}

    def read():
        return {'marker': 'v1', 'sources': sources}

    with db.transaction() as connection:
        snapshot.persist_snapshot(connection, company, period, read,
                                  policy_hash='p' * 10, timezone='Europe/Madrid')


def auth(token):
    return {'Authorization': f'Bearer {token}'}


def test_prepare_is_idempotent_and_reports_the_sector(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db)
    with http as client:
        first = client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                            json={'period': '2026-10'})
        again = client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                            json={'period': '2026-10'})
    assert first.status_code == 200
    assert first.json()['created'] is True and again.json()['created'] is False
    body = first.json()['closure']
    assert body['sector']['id'] == 'hosteleria'
    assert body['result']['totals'] == {'employees': 1, 'minutes': 465, 'issues': 0}
    assert body['content_hash'] == again.json()['closure']['content_hash']


def test_prepare_needs_a_snapshot(tmp_path, monkeypatch):
    _, http = setup(tmp_path, monkeypatch)
    with http as client:
        response = client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                               json={'period': '2026-09'})
    assert response.status_code == 404
    assert response.json()['detail']['code'] == 'not_found'


def test_viewer_cannot_prepare_a_closure(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db)
    with http as client:
        response = client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(VIEWER),
                               json={'period': '2026-10'})
    assert response.status_code == 403
    assert response.json()['detail']['code'] == 'forbidden'


def test_a_disabled_company_stays_closed(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db)
    with http as client:
        response = client.post(f'/api/companies/{OTHER}/rrhh/closures', headers=auth(OWNER),
                               json={'period': '2026-10'})
    assert response.status_code == 404


def test_export_requires_an_approval_first(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db)
    with http as client:
        client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                    json={'period': '2026-10'})
        response = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/export',
                               headers=auth(OWNER))
    assert response.status_code == 409
    assert response.json()['detail']['code'] == 'approval_required'


def test_the_preparer_cannot_approve_through_the_api(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db)
    with http as client:
        client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                    json={'period': '2026-10'})
        response = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/approve',
                               headers=auth(OWNER),
                               json={'justification': 'Me lo apruebo yo mismo sin revisar'})
    assert response.status_code == 403
    assert response.json()['detail']['code'] == 'separation_of_duties'


def test_full_flow_approves_and_exports_once(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db)
    with http as client:
        client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                    json={'period': '2026-10'})
        signed = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/approve',
                             headers=auth(REVIEWER),
                             json={'justification': 'Revisados fichajes y pausas del mes'})
        first = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/export',
                            headers=auth(REVIEWER))
        again = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/export',
                            headers=auth(REVIEWER))
        read = client.get(f'/api/companies/{CID}/rrhh/closures/2026-10', headers=auth(VIEWER))
    assert signed.status_code == 200 and signed.json()['approval']['approved_by'] == 'luis-rev'
    assert first.status_code == 200 and first.json()['created'] is True
    assert again.status_code == 200 and again.json()['created'] is False
    manifest = first.json()['export']['manifest']
    assert manifest['totals'] == {'employees': 1, 'minutes': 465, 'issues': 0}
    assert manifest['approval_id'] == signed.json()['approval']['id']
    assert read.json()['closure']['prepared_by'] == 'owner'


def test_unreviewed_issues_are_reported_by_the_api(tmp_path, monkeypatch):
    db, http = setup(tmp_path, monkeypatch)
    seed(db, employees=[{'ref': 'e1', 'punches': [PUNCHES[0]], 'absences': []}])
    with http as client:
        client.post(f'/api/companies/{CID}/rrhh/closures', headers=auth(OWNER),
                    json={'period': '2026-10'})
        blocked = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/approve',
                             headers=auth(REVIEWER),
                             json={'justification': 'Cierro el mes sin mirar incidencias'})
        accepted = client.post(f'/api/companies/{CID}/rrhh/closures/2026-10/approve',
                               headers=auth(REVIEWER),
                               json={'justification': 'Entrada sin salida revisada con la persona',
                                     'accepted_issues': ['incomplete_punch', 'missing_punch']})
    assert blocked.status_code == 409
    assert blocked.json()['detail']['code'] == 'unreviewed_issues'
    assert accepted.status_code == 200
    assert accepted.json()['approval']['acknowledged'] == {'incomplete_punch': 1, 'missing_punch': 1}
