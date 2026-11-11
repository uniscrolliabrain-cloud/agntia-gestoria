"""Opaque, expiring browser sessions backed by the application's SQLite DB."""

import hashlib
import secrets
import threading
import time
from collections import OrderedDict

from fastapi import HTTPException


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


def initialize(db):
    with db.transaction() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS browser_sessions("
            "session_hash TEXT PRIMARY KEY, token_hash TEXT NOT NULL, expires_at REAL NOT NULL)"
        )


def issue(db, token):
    session = secrets.token_urlsafe(32)
    with db.transaction() as connection:
        connection.execute("DELETE FROM browser_sessions WHERE expires_at <= ?", (time.time(),))
        connection.execute("INSERT INTO browser_sessions VALUES(?,?,?)",
                           (fingerprint(session), fingerprint(token), time.time() + 28800))
    return session


def resolve(db, session):
    with db.connection() as connection:
        row = connection.execute(
            "SELECT token_hash FROM browser_sessions WHERE session_hash=? AND expires_at>?",
            (fingerprint(session), time.time()),
        ).fetchone()
    return row["token_hash"] if row else None


def revoke(db, session):
    with db.transaction() as connection:
        connection.execute("DELETE FROM browser_sessions WHERE session_hash=?", (fingerprint(session),))


class LoginLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._attempts = OrderedDict()

    def check(self, client):
        moment = time.monotonic()
        with self._lock:
            attempts = [stamp for stamp in self._attempts.pop(client, []) if moment - stamp < 60]
            if len(attempts) >= 10:
                self._attempts[client] = attempts
                raise HTTPException(429, "Demasiados intentos. Espera un minuto.", headers={"Retry-After": "60"})
            attempts.append(moment)
            self._attempts[client] = attempts
            while len(self._attempts) > 10000:
                self._attempts.popitem(last=False)
