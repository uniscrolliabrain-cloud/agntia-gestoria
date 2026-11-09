import argparse
import json
import os
from datetime import datetime,timedelta,timezone
from ...storage import Database,canonical,digest,now,uid,identifier
from .. import policy
from ..errors import IntegrationError,reject
from .evidence import event


class Jobs:
    def enqueue(self,actor,cid,operation,payload,key,correlation):
        connection,_=self.scope(actor,cid,'imports.run');hash_=digest({'operation':operation,'payload':payload})
        if operation not in ('preview','import'):reject('validation','Tipo de trabajo no permitido',422)
        with self.db.transaction() as c:
            old=c.execute('SELECT payload_hash,body FROM idempotency_keys WHERE company_id=? AND connection_id=? AND operation=? AND key=?',(cid,connection['id'],'job',key)).fetchone()
            if old:
                if old['payload_hash']!=hash_:reject('idempotency_conflict','Clave reutilizada con contenido distinto',409)
                return json.loads(old['body'])
            job={'id':uid(),'company_id':cid,'connection_id':connection['id'],'tenant_id':connection['tenant_id'],'actor_id':actor.id,'operation':operation,'payload':payload,'idempotency_key':key,'connection_revision':connection['revision'],'state':'pending','attempts':0,'revision':0,'correlation_id':correlation,'created_at':now(),'result':None,'error':None}
            c.execute('INSERT INTO sync_jobs VALUES(?,?,?,?,?,?,?,?,?,?)',(job['id'],cid,connection['id'],'pending',0,0,None,None,now(),canonical(job)))
            result={'job_id':job['id'],'state':'pending'}
            c.execute('INSERT INTO idempotency_keys VALUES(?,?,?,?,?,?,?)',(cid,connection['id'],'job',key,hash_,'pending',canonical(result)))
            self.db.audit(c,cid,actor,'integration.job.enqueued',job['id'],job)
        return result

    def job(self,actor,cid,job_id):
        policy.authorize(actor,cid,policy.tenant_for(actor,cid),'jobs.read')
        with self.db.connection() as c:
            row=c.execute('SELECT body FROM sync_jobs WHERE id=? AND company_id=?',(identifier(job_id),cid)).fetchone()
            if not row:reject('not_found','Recurso no encontrado',404)
            job=json.loads(row['body'])
        if job['tenant_id']!=policy.tenant_for(actor,cid):reject('not_found','Recurso no encontrado',404)
        return {k:v for k,v in job.items() if k not in ('payload','idempotency_key')}

    def run_one(self):
        if not policy.enabled():return None
        lease_owner=uid();clock=now();lease=(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()
        with self.db.transaction() as c:
            row=c.execute("SELECT j.* FROM sync_jobs j WHERE ((j.state='pending' AND j.available_at<=?) OR (j.state='running' AND j.lease_until<?)) AND NOT EXISTS(SELECT 1 FROM sync_jobs other WHERE other.connection_id=j.connection_id AND other.id!=j.id AND other.state='running' AND other.lease_until>=?) ORDER BY j.rowid LIMIT 1",(clock,clock,clock)).fetchone()
            if not row:return None
            job=json.loads(row['body']);job.update(state='running',attempts=row['attempts']+1,revision=row['revision']+1)
            c.execute('UPDATE sync_jobs SET state=?,attempts=?,revision=?,lease_until=?,lease_owner=?,body=? WHERE id=?',('running',job['attempts'],job['revision'],lease,lease_owner,canonical(job),job['id']))
        def heartbeat():
            with self.db.transaction() as c:
                result=c.execute('UPDATE sync_jobs SET lease_until=? WHERE id=? AND lease_owner=? AND state=?',((datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat(),job['id'],lease_owner,'running'))
                if result.rowcount!=1:reject('lease_lost','Trabajo reclamado por otro worker',409)
        error=None
        try:
            if job['attempts']>3:reject('retry_budget','Presupuesto de recuperación agotado',409)
            actor=policy.actor_for_job(job['actor_id']);connection,_=self.scope(actor,job['company_id'],'imports.run',job['connection_id'])
            if connection['revision']!=job['connection_revision']:reject('connection_changed','Conexión modificada desde el encolado',409)
            if job['operation']=='preview':result=self.preview(actor,job['company_id'],job['payload']['resource'],job['payload']['full'],job['correlation_id'],heartbeat)
            else:result=self.import_stages(actor,job['company_id'],job['payload']['staging_ids'],job['idempotency_key'],job['correlation_id'])
            state='succeeded'
        except Exception as exc:
            if isinstance(exc,IntegrationError):error=exc.public(job['correlation_id']);state='reconciliation_required' if exc.uncertain else 'pending' if exc.retryable and job['attempts']<3 else 'failed'
            else:error={'code':'job_blocked','message':'Trabajo bloqueado; revisar permisos y evidencia interna','retryable':False};state='blocked'
            result=None
        with self.db.transaction() as c:
            row=c.execute('SELECT lease_owner FROM sync_jobs WHERE id=?',(job['id'],)).fetchone()
            if row['lease_owner']!=lease_owner:return {'job_id':job['id'],'state':'lease_lost'}
            job.update(state=state,result=result,error=error,revision=job['revision']+1,completed_at=now())
            c.execute('UPDATE sync_jobs SET state=?,revision=?,lease_until=NULL,lease_owner=NULL,available_at=?,body=? WHERE id=?',(state,job['revision'],(datetime.now(timezone.utc)+timedelta(seconds=min(60,2**job['attempts']))).isoformat(),canonical(job),job['id']))
            if error:
                # A failed/revoked actor never gains owner privileges to emit a business mutation.
                self.db.audit(c,job['company_id'],type('Principal',(),{'id':job['actor_id'],'role':'worker'})(),'integration.job.failed',job['id'],{'correlation_id':job['correlation_id'],'code':error['code']})
        return {'job_id':job['id'],'state':state,'result':result,'error':error}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--once',action='store_true');parser.add_argument('--data-dir',default=os.getenv('GESTORIA_DATA_DIR','./data'));args=parser.parse_args()
    from dotenv import load_dotenv
    load_dotenv()
    from ..migrations import migrate
    from .adapter import Adapter
    import time
    db=Database(args.data_dir);migrate(db);adapter=Adapter(db)
    while True:
        result=adapter.run_one()
        if result:print(json.dumps({'job_id':result['job_id'],'state':result['state']}),flush=True)
        if args.once:return
        if not result:time.sleep(1)


if __name__=='__main__':main()
