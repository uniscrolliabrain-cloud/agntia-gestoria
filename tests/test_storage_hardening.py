import pytest

from agntia_gestoria.storage import Database, canonical

CID = 'a' * 32
OTHER = 'b' * 32


def database(tmp_path):
    db = Database(str(tmp_path))
    with db.transaction() as connection:
        for cid in (CID, OTHER):
            connection.execute('INSERT INTO companies(id,body) VALUES(?,?)',
                               (cid, canonical({'id': cid, 'name': cid[:4]})))
    return db


def test_put_updates_the_logical_key_on_conflict(tmp_path):
    db = database(tmp_path)
    body = {'id': '1' * 32, 'company_id': CID, 'value': 1}
    with db.transaction() as connection:
        Database.put(connection, CID, 'demo', body, unique_key='k1')
        Database.put(connection, CID, 'demo', dict(body, value=2), unique_key='k2')
        row = connection.execute(
            'SELECT body,unique_key FROM objects WHERE id=?', (body['id'],)).fetchone()
    assert row['unique_key'] == 'k2'
    assert '"value":2' in row['body']


def test_put_refuses_an_identifier_from_another_company(tmp_path):
    db = database(tmp_path)
    body = {'id': '2' * 32, 'company_id': CID, 'value': 1}
    with db.transaction() as connection:
        Database.put(connection, CID, 'demo', body)
        with pytest.raises(PermissionError):
            Database.put(connection, OTHER, 'demo', dict(body, company_id=OTHER))
        with pytest.raises(PermissionError):
            Database.put(connection, OTHER, 'otro', dict(body, company_id=OTHER))


def test_put_refuses_a_body_from_another_company(tmp_path):
    db = database(tmp_path)
    with db.transaction() as connection:
        with pytest.raises(ValueError):
            Database.put(connection, CID, 'demo', {'id': '3' * 32, 'company_id': OTHER})
