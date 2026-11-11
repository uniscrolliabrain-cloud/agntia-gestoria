import logging
import sqlite3
import json
import time
import uuid
from datetime import datetime,timezone
from decimal import Decimal

from ...auth import company_access
from ...storage import canonical,digest,identifier,now,uid
from .. import policy
from ..errors import IntegrationError,reject
from ..registry import load_server
from .transport import Client
from .discovery import discover
from .evidence import event,verify_audit


class GuardedClient:
    def __init__(self,service,actor,cid,connection,capability,validating=False):
        self.service=service;self.actor=actor;self.cid=cid;self.connection=connection;self.capability=capability;self.validating=validating
    def call(self,model,method,payload=None):
        connection,server=self.service.scope(self.actor,self.cid,self.capability,self.connection['id'],not self.validating)
        start=time.monotonic();success=False;code='ok'
        try:
            client=self.service.client_factory(server)
            if isinstance(client,Client):
                client.before_request=lambda:self.service.scope(self.actor,self.cid,self.capability,self.connection['id'],not self.validating)
            result=client.call(model,method,payload);success=True;return result
        except IntegrationError as exc:
            code=exc.code
            if code in ('provider_auth','scope_violation','unsafe_principal'):
                with self.service.db.transaction() as c:
                    current=self.service._connection(c,self.cid,connection['id'])
                    if current['state']=='ready':
                        current.update(state='degraded',revision=current['revision']+1);self.service.save_connection(c,current)
                    event(self.service.db,c,current,self.actor,'connection.degraded',{'code':code},str(uuid.uuid4()))
            raise
        finally:
            try:
                with self.service.db.transaction() as c:
                    c.execute('INSERT INTO integration_metrics(connection_id,operation,duration_ms,success,code,at) VALUES(?,?,?,?,?,?)',(connection['id'],model+'.'+method,(time.monotonic()-start)*1000,int(success),code,now()))
            except sqlite3.Error:
                logging.getLogger(__name__).warning("integration_metrics_write_failed")


class Service:
    def __init__(self,db,client_factory=None):
        self.db=db;self.client_factory=client_factory or Client

    def scope(self,actor,cid,capability,connection_id=None,ready=True):
        identifier(cid);tenant=policy.tenant_for(actor,cid);policy.authorize(actor,cid,tenant,capability)
        with self.db.connection() as c:
            self.db.company(c,cid)
            row=c.execute('SELECT * FROM provider_connections WHERE company_id=? AND id=?',(cid,identifier(connection_id))).fetchone() if connection_id else c.execute("SELECT * FROM provider_connections WHERE company_id=? ORDER BY (state!='disabled') DESC,rowid DESC LIMIT 1",(cid,)).fetchone()
            if not row:reject('not_configured','Conexión Odoo no configurada',424)
            connection=json.loads(row['body'])
        if connection['tenant_id']!=tenant:reject('not_found','Recurso no encontrado',404)
        server=load_server(connection['server_ref'])
        if server.gestoria_company_id!=cid or server.tenant_id!=tenant or server.odoo_company_id!=connection['remote_company']:reject('not_found','Recurso no encontrado',404)
        if ready:
            if connection.get('instance_id') and connection['instance_id']!=server.expected_instance_id:reject('configuration_changed','Cambio de instancia: desactivar y crear una conexión nueva',409)
            if connection['state']!='ready':reject('not_ready','Conexión Odoo no validada o desactivada',424)
            if digest(server.model_dump(mode='json'))!=connection['configuration_hash']:reject('configuration_changed','Configuración cambiada; validar la conexión de nuevo',409)
            report=connection.get('report',{})
            if not report.get('expires_at') or datetime.fromisoformat(report['expires_at'])<datetime.now(timezone.utc):reject('stale_capabilities','Capacidades caducadas; validar de nuevo',424)
        return connection,server

    def client(self,actor,cid,capability,connection,validating=False):return GuardedClient(self,actor,cid,connection,capability,validating)

    @staticmethod
    def public(connection):
        return {'connection_id':connection['id'],'gestoria_company_id':connection['company_id'],'tenant_id':connection['tenant_id'],'provider':'odoo_community','provider_version':'19.0','state':connection['state'],'revision':connection['revision'],'capabilities':connection.get('report',{}).get('capabilities',[]),'checked_at':connection.get('report',{}).get('checked_at'),'expires_at':connection.get('report',{}).get('expires_at')}

    def save_connection(self,c,connection):
        c.execute('UPDATE provider_connections SET state=?,revision=?,body=? WHERE id=?',(connection['state'],connection['revision'],canonical(connection),connection['id']))

    def create_connection(self,actor,cid,request,correlation):
        tenant=policy.tenant_for(actor,cid);policy.authorize(actor,cid,tenant,'connections.manage')
        server=load_server(request.server_ref)
        if server.gestoria_company_id!=cid or server.tenant_id!=tenant:reject('not_found','Recurso no encontrado',404)
        with self.db.transaction() as c:
            self.db.company(c,cid)
            if c.execute("SELECT 1 FROM provider_connections WHERE company_id=? AND state!='disabled'",(cid,)).fetchone():reject('conflict','Ya existe una conexión activa',409)
            connection={'id':uid(),'company_id':cid,'tenant_id':tenant,'server_ref':request.server_ref,'remote_company':server.odoo_company_id,'state':'pending_validation','revision':0,'created_at':now(),'configuration_hash':digest(server.model_dump(mode='json'))}
            c.execute('INSERT INTO provider_connections VALUES(?,?,?,?,?,?,?,?)',(connection['id'],cid,tenant,request.server_ref,server.odoo_company_id,connection['state'],0,canonical(connection)))
            event(self.db,c,connection,actor,'review.required',{'operation':'binding','revision':0},correlation)
        return self.public(connection)

    def validate(self,actor,cid,body,correlation):
        connection,server=self.scope(actor,cid,'connections.manage',ready=False)
        if connection.get('instance_id') and connection['instance_id']!=server.expected_instance_id:reject('configuration_changed','No se puede reutilizar un binding para otra instancia',409)
        if connection['revision']!=body.revision:reject('conflict','Revisión de conexión incorrecta',409)
        if connection['state']=='disabled':reject('conflict','Crea una conexión nueva tras desactivar',409)
        try:report=discover(self.client(actor,cid,'connections.manage',connection,True),server)
        except IntegrationError as exc:
            with self.db.transaction() as c:
                current=self._connection(c,cid,connection['id'])
                if current['revision']==body.revision:
                    current.update(state='degraded',revision=current['revision']+1);self.save_connection(c,current)
                event(self.db,c,current,actor,'connection.degraded',{'code':exc.code},correlation)
            raise
        with self.db.transaction() as c:
            current=self._connection(c,cid,connection['id'])
            if current['revision']!=body.revision:reject('conflict','La conexión cambió durante discovery',409)
            company=self.db.company(c,cid);local=''.join(company.get('nif','').upper().split());remote=''.join(report.pop('identity_vat').upper().split())
            if (not local or not remote or local!=remote) and (not body.confirm_fiscal_identity or len(body.notes)<5):reject('identity_confirmation_required','Identidad fiscal incompleta o distinta; requiere confirmación humana y motivo',409)
            for row in c.execute("SELECT body FROM provider_connections WHERE id!=? AND state!='disabled'",(current['id'],)):
                other=json.loads(row['body'])
                if other.get('instance_id')==server.expected_instance_id and (other['tenant_id']!=current['tenant_id'] or not server.allow_multi_company):reject('binding_conflict','Instancia ya vinculada a otro ámbito',409)
            current.update(state='ready',revision=current['revision']+1,instance_id=server.expected_instance_id,report=report,configuration_hash=digest(server.model_dump(mode='json')),binding_confirmation={'actor_id':actor.id,'at':now(),'notes':body.notes,'identity_hash':digest({'local':local,'remote':remote})})
            self.save_connection(c,current);event(self.db,c,current,actor,'sync.completed',{'operation':'discovery','capabilities':report['capabilities']},correlation)
        return self.public(current)

    def disable(self,actor,cid,revision,correlation):
        connection,_=self.scope(actor,cid,'connections.manage',ready=False)
        with self.db.transaction() as c:
            current=self._connection(c,cid,connection['id'])
            if current['revision']!=revision:reject('conflict','Revisión incorrecta',409)
            current.update(state='disabled',revision=revision+1);self.save_connection(c,current)
            event(self.db,c,current,actor,'connection.degraded',{'code':'disabled_by_owner'},correlation)
        return self.public(current)

    @staticmethod
    def _connection(c,cid,connection_id):
        row=c.execute('SELECT body FROM provider_connections WHERE company_id=? AND id=?',(cid,identifier(connection_id))).fetchone()
        if not row:reject('not_found','Recurso no encontrado',404)
        return json.loads(row['body'])

    def require_capability(self,connection,name):
        if name not in connection.get('report',{}).get('capabilities',[]):reject('unsupported','Capacidad no confirmada en esta instalación',424)

    def list_scoped(self,actor,cid,table,capability):
        if table not in ('integration_staging','external_links','integration_conflicts','integration_outbox','sync_jobs'):raise ValueError('Invalid internal table')
        connection,_=self.scope(actor,cid,capability,ready=False)
        with self.db.connection() as c:
            return [json.loads(r['body']) for r in c.execute('SELECT body FROM '+table+' WHERE company_id=? AND connection_id=? ORDER BY rowid DESC',(cid,connection['id']))]

    def capabilities(self,actor,cid):
        connection,_=self.scope(actor,cid,'health',ready=False)
        report=connection.get('report',{})
        return {**self.public(connection),'stale':not report.get('expires_at') or datetime.fromisoformat(report['expires_at'])<datetime.now(timezone.utc),'evidence_hash':report.get('evidence_hash'),'unsupported':report.get('unsupported',[]),'remote_publication':False,'official_filing':False}

    def audit_integrity(self,actor,cid):
        self.scope(actor,cid,'health',ready=False)
        with self.db.connection() as c:return verify_audit(self.db,c,cid)

    def metrics(self,actor,cid):
        connection,_=self.scope(actor,cid,'metrics.read',ready=False)
        with self.db.connection() as c:
            rows=c.execute('SELECT operation,duration_ms,success,code FROM integration_metrics WHERE connection_id=? ORDER BY id DESC LIMIT 10000',(connection['id'],)).fetchall()
            pending=c.execute("SELECT count(*) FROM integration_conflicts WHERE connection_id=? AND state='open'",(connection['id'],)).fetchone()[0]
        times=sorted(r['duration_ms'] for r in rows);count=len(rows)
        groups={}
        for row in rows:
            group=groups.setdefault(row['operation'],{'durations':[],'failures':0})
            group['durations'].append(row['duration_ms']);group['failures']+=int(not row['success'])
        ranked=sorted(groups.items(),key=lambda item:(-len(item[1]['durations']),item[0]))[:25]
        return {'sample_size':count,'latency_p50_ms':times[int((count-1)*.5)] if count else None,'latency_p95_ms':times[int((count-1)*.95)] if count else None,'failures':sum(not r['success'] for r in rows),'open_conflicts':pending,'by_operation':{name:self._summary(values) for name,values in ranked},'cost_measured':False,'notice':'Muestra de últimas 10000 llamadas; no es una estimación de coste ni SLA.'}

    @staticmethod
    def _summary(values):
        times=sorted(values['durations']);count=len(times)
        return {'sample_size':count,'latency_p50_ms':times[int((count-1)*.5)] if count else None,'latency_p95_ms':times[int((count-1)*.95)] if count else None,'failures':values['failures']}
