import json
import random
import threading
import time
from decimal import Decimal
from urllib.parse import urlsplit
import httpx
from ..errors import IntegrationError,reject
from ..registry import credentials,resolve_target

READ={('agntia.bridge',m) for m in ('server_info','invoice_snapshots','attachment_metadata','attachment_content','operation_status','preview_invoice')}
READ|={(m,'search_read') for m in ('res.partner','account.move','account.move.line','account.tax','account.journal','account.account','res.currency','ir.module.module')}
READ|={(m,'fields_get') for m in ('res.partner','account.move','account.move.line','account.tax','account.journal','account.account','ir.attachment')}
WRITE={('agntia.bridge','execute_approved')}
_LOCK=threading.Lock();_FAILURES={}


def json_values(value):
    if isinstance(value,Decimal):return str(value)
    if isinstance(value,dict):return {k:json_values(v) for k,v in value.items()}
    if isinstance(value,list):return [json_values(v) for v in value]
    return value


class Client:
    def __init__(self,server,transport=None,resolver=None,sleep=time.sleep):
        self.server=server;self.resolver=resolver;self.sleep=sleep;self.transport=transport;self.before_request=None

    def call(self,model,method,payload=None):
        pair=(model,method)
        if pair not in READ|WRITE:reject('forbidden','Operación ORM no permitida',403)
        writing=pair in WRITE
        if writing and not self.server.write_enabled:reject('forbidden','Escritura Odoo desactivada',403)
        supplied=payload or {}
        if any(k in supplied for k in ('context','allowed_company_ids','sudo','database','base_url')):reject('validation','Parámetros reservados',422)
        key=self.server.base_url+'|'+self.server.expected_instance_id
        with _LOCK:
            failures,until=_FAILURES.get(key,(0,0))
            if until>time.monotonic():reject('circuit_open','Proveedor temporalmente no disponible',503)
        for attempt in range(1 if writing else 3):
            try:
                result=self._once(model,method,supplied)
                with _LOCK:_FAILURES.pop(key,None)
                return result
            except IntegrationError as exc:
                if exc.retryable:
                    with _LOCK:
                        failures=_FAILURES.get(key,(0,0))[0]+1
                        _FAILURES[key]=(failures,time.monotonic()+30 if failures>=5 else 0)
                if writing or not exc.retryable or attempt==2:raise
                self.sleep(.1*(2**attempt)+random.random()*.1)

    def _once(self,model,method,payload):
        if self.before_request:self.before_request()
        writing=(model,method) in WRITE
        address=resolve_target(self.server,self.resolver)
        url=httpx.URL(self.server.base_url).copy_with(host=address,path=f'/json/2/{model}/{method}')
        original=urlsplit(self.server.base_url);host=original.hostname
        host_header=('['+host+']' if ':' in host else host)+((':'+str(original.port)) if original.port else '')
        body={**payload,'context':{'allowed_company_ids':[self.server.odoo_company_id]}}
        headers={'Authorization':'bearer '+credentials(self.server).get_secret_value(),'X-Odoo-Database':self.server.database,'Host':host_header,'Content-Type':'application/json','User-Agent':'agntia-gestoria/odoo19-v1'}
        try:
            with httpx.Client(transport=self.transport,timeout=httpx.Timeout(15,connect=4),follow_redirects=False,trust_env=False,limits=httpx.Limits(max_connections=4,max_keepalive_connections=2)) as client:
                with client.stream('POST',url,headers=headers,json=body,extensions={'sni_hostname':host}) as response:
                    status=response.status_code
                    if status in (401,403):raise IntegrationError('provider_auth','Credencial o permisos Odoo insuficientes',424)
                    if status==404:raise IntegrationError('unsupported','Capacidad Odoo no disponible',424)
                    if status==429:raise IntegrationError('rate_limit','Proveedor limitado temporalmente',429,True,writing)
                    if status>=500:raise IntegrationError('provider_unavailable','Proveedor no disponible',503,True,writing)
                    if 300<=status<400:raise IntegrationError('redirect_blocked','Redirección Odoo rechazada',502,False,writing)
                    if status>=400:raise IntegrationError('provider_validation','Operación rechazada por Odoo',422,False,writing)
                    raw=bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw)>self.server.max_response_bytes:raise IntegrationError('response_too_large','Respuesta Odoo demasiado grande',502,False,writing)
                    try:value=json.loads(raw,parse_float=Decimal,parse_constant=lambda _:(_ for _ in ()).throw(ValueError()))
                    except (ValueError,UnicodeError):raise IntegrationError('invalid_response','Respuesta Odoo inválida',502,False,writing) from None
                    return json_values(value)
        except IntegrationError:raise
        except httpx.TimeoutException:raise IntegrationError('timeout','Tiempo de espera Odoo agotado',504,True,writing) from None
        except httpx.HTTPError:raise IntegrationError('network','Conexión Odoo no disponible',503,True,writing) from None
