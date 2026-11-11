import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def uid():
    return uuid.uuid4().hex


def identifier(value):
    if not re.fullmatch(r"[a-f0-9]{32}", value):
        raise ValueError("Identificador inválido")
    return value


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Database:
    def __init__(self, directory):
        self.root = Path(directory).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "gestoria.sqlite3"
        with self.connection() as connection:
            connection.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS companies(id TEXT PRIMARY KEY, body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS objects(id TEXT PRIMARY KEY, company_id TEXT NOT NULL REFERENCES companies(id), kind TEXT NOT NULL, body TEXT NOT NULL, unique_key TEXT, UNIQUE(company_id,unique_key));
                CREATE INDEX IF NOT EXISTS by_company ON objects(company_id,kind);
                CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT,company_id TEXT NOT NULL REFERENCES companies(id),body TEXT NOT NULL,hash TEXT NOT NULL);
            """)

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @contextmanager
    def transaction(self):
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            yield connection

    @staticmethod
    def company(connection, cid):
        row = connection.execute("SELECT body FROM companies WHERE id=?", (identifier(cid),)).fetchone()
        if not row:
            raise FileNotFoundError()
        return json.loads(row["body"])

    @staticmethod
    def get(connection, cid, oid, kind):
        row = connection.execute("SELECT body FROM objects WHERE company_id=? AND id=? AND kind=?", (identifier(cid), identifier(oid), kind)).fetchone()
        if not row:
            raise FileNotFoundError()
        return json.loads(row["body"])

    @staticmethod
    def list(connection, cid, kind):
        return [json.loads(row["body"]) for row in connection.execute("SELECT body FROM objects WHERE company_id=? AND kind=? ORDER BY rowid DESC", (identifier(cid), kind))]

    @staticmethod
    def put(connection, cid, kind, body, unique_key=None):
        identifier(cid)
        identifier(body["id"])
        if body.get("company_id", cid) != cid:
            raise ValueError("Empresa del objeto incompatible")
        result = connection.execute(
            "INSERT INTO objects(id,company_id,kind,body,unique_key) VALUES(?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET body=excluded.body, "
            "unique_key=COALESCE(excluded.unique_key,objects.unique_key) "
            "WHERE objects.company_id=excluded.company_id AND objects.kind=excluded.kind",
            (body["id"], cid, kind, canonical(body), unique_key),
        )
        if result.rowcount != 1:
            raise FileNotFoundError()

    @staticmethod
    def audit(connection, cid, actor, action, object_id, body):
        previous = connection.execute("SELECT hash FROM audit WHERE company_id=? ORDER BY seq DESC LIMIT 1", (cid,)).fetchone()
        event = {"at": now(), "actor_id": actor.id, "actor_role": actor.role, "action": action, "object_id": object_id,
                 "content_hash": digest(body), "previous_hash": previous["hash"] if previous else "0"*64}
        hashed = digest(event)
        connection.execute("INSERT INTO audit(company_id,body,hash) VALUES(?,?,?)", (cid, canonical(event), hashed))

    @staticmethod
    def audit_log(connection, cid):
        return [{**json.loads(row["body"]), "hash": row["hash"], "sequence": row["seq"]} for row in connection.execute("SELECT * FROM audit WHERE company_id=? ORDER BY seq", (identifier(cid),))]
