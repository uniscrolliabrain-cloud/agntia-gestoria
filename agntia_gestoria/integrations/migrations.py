"""Additive integration schema. No executescript implicit commits or destructive downgrade."""
import hashlib
import sqlite3
from pathlib import Path
from ..storage import now,uid

DDL=[
'''CREATE TABLE IF NOT EXISTS integration_migrations(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL)''',
'''CREATE TABLE provider_connections(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),tenant_id TEXT NOT NULL,server_ref TEXT NOT NULL,remote_company INTEGER NOT NULL,state TEXT NOT NULL,revision INTEGER NOT NULL,body TEXT NOT NULL)''',
'''CREATE TABLE external_links(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),model TEXT NOT NULL,external_id TEXT NOT NULL,local_kind TEXT NOT NULL,local_id TEXT NOT NULL,source_hash TEXT NOT NULL,body TEXT NOT NULL,UNIQUE(connection_id,model,external_id,local_kind),UNIQUE(company_id,local_kind,local_id))''',
'''CREATE TABLE integration_staging(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),model TEXT NOT NULL,external_id TEXT NOT NULL,source_hash TEXT NOT NULL,state TEXT NOT NULL,body TEXT NOT NULL,UNIQUE(connection_id,model,external_id,source_hash))''',
'''CREATE TABLE sync_jobs(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),state TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,revision INTEGER NOT NULL DEFAULT 0,lease_until TEXT,lease_owner TEXT,available_at TEXT NOT NULL,body TEXT NOT NULL)''',
'''CREATE TABLE sync_cursors(connection_id TEXT NOT NULL REFERENCES provider_connections(id),resource TEXT NOT NULL,body TEXT NOT NULL,PRIMARY KEY(connection_id,resource))''',
'''CREATE TABLE integration_outbox(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),state TEXT NOT NULL,body TEXT NOT NULL)''',
'''CREATE TABLE integration_inbox(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),body TEXT NOT NULL)''',
'''CREATE TABLE idempotency_keys(company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),operation TEXT NOT NULL,key TEXT NOT NULL,payload_hash TEXT NOT NULL,state TEXT NOT NULL,body TEXT NOT NULL,PRIMARY KEY(company_id,connection_id,operation,key))''',
'''CREATE TABLE integration_conflicts(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),state TEXT NOT NULL,revision INTEGER NOT NULL,body TEXT NOT NULL)''',
'''CREATE TABLE integration_proposals(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),connection_id TEXT NOT NULL REFERENCES provider_connections(id),revision INTEGER NOT NULL,state TEXT NOT NULL,body TEXT NOT NULL)''',
'''CREATE TABLE integration_approvals(id TEXT PRIMARY KEY,company_id TEXT NOT NULL REFERENCES companies(id),proposal_id TEXT NOT NULL REFERENCES integration_proposals(id),body TEXT NOT NULL)''',
'''CREATE TABLE integration_metrics(id INTEGER PRIMARY KEY AUTOINCREMENT,connection_id TEXT NOT NULL,operation TEXT NOT NULL,duration_ms REAL NOT NULL,success INTEGER NOT NULL,code TEXT NOT NULL,at TEXT NOT NULL)''',
"CREATE UNIQUE INDEX one_write_per_proposal ON idempotency_keys(company_id,connection_id,json_extract(body,'$.proposal_id')) WHERE operation='write'",
"CREATE UNIQUE INDEX one_active_connection ON provider_connections(company_id) WHERE state!='disabled'",
'''CREATE INDEX jobs_ready ON sync_jobs(state,available_at,lease_until)''',
'''CREATE INDEX conflicts_by_company ON integration_conflicts(company_id,state)''',
]


def migrate(db):
    with db.connection() as c:
        exists=c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='integration_migrations'").fetchone()
        if exists and c.execute('SELECT 1 FROM integration_migrations WHERE version=1').fetchone():return None
    backups=db.root/'migration-backups';backups.mkdir(exist_ok=True)
    target=backups/('before-odoo-v1-'+uid()+'.sqlite3')
    with sqlite3.connect(db.path) as source,sqlite3.connect(target) as destination:source.backup(destination)
    with db.transaction() as c:
        c.execute(DDL[0])
        if c.execute('SELECT 1 FROM integration_migrations WHERE version=1').fetchone():return target
        for statement in DDL[1:]:c.execute(statement)
        c.execute('INSERT INTO integration_migrations VALUES(1,?)',(now(),))
    return target
