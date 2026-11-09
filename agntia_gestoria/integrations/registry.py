import ipaddress
import json
import os
import socket
from urllib.parse import urlsplit
from pydantic import Field,SecretStr,field_validator
from decimal import Decimal
from ..models import Model
from .contracts import HexId,Opaque
from .errors import reject


class Server(Model):
    base_url:str
    database:str=Field(min_length=1,max_length=100,pattern=r'^[a-zA-Z0-9_-]+$')
    approval_signing_key_env:str=Field(default='ODOO_BRIDGE_SIGNING_KEY',pattern=r'^[A-Z][A-Z0-9_]+$')
    api_key_env:str=Field(pattern=r'^[A-Z][A-Z0-9_]+$')
    gestoria_company_id:HexId
    tenant_id:Opaque
    odoo_company_id:int=Field(gt=0)
    expected_source_revision:str=Field(default='60657b50d171ddf84ab58717fdee5ac26031065b',pattern=r'^[a-f0-9]{40}$')
    expected_instance_id:str=Field(pattern=r'^[a-f0-9]{32}$')
    allowed_networks:list[str]=Field(min_length=1,max_length=30)
    allow_insecure_test:bool=False
    allow_multi_company:bool=False
    write_enabled:bool=False
    allowed_partner_ids:list[int]=Field(default_factory=list)
    allowed_journal_ids:list[int]=Field(default_factory=list)
    allowed_account_ids:list[int]=Field(default_factory=list)
    allowed_tax_ids:list[int]=Field(default_factory=list)
    tax_mappings:dict=Field(default_factory=dict)
    max_response_bytes:int=Field(default=8*1024*1024,ge=1024,le=16*1024*1024)


    @field_validator('allowed_partner_ids','allowed_journal_ids','allowed_account_ids','allowed_tax_ids')
    @classmethod
    def identifiers(cls,value):
        if len(value)>10000 or len(value)!=len(set(value)) or any(type(i)!=int or i<=0 for i in value):raise ValueError('Invalid configured ids')
        return value

    @field_validator('tax_mappings')
    @classmethod
    def mappings(cls,value):
        if len(value)>10000:raise ValueError('Too many tax mappings')
        for key,item in value.items():
            if not str(key).isdigit() or int(key)<=0 or not isinstance(item,dict) or set(item)!={'tax_kind','rate'} or item['tax_kind'] not in ('iva','igic','ipsi') or not isinstance(item['rate'],str):raise ValueError('Invalid mapping')
            try:rate=Decimal(item['rate'])
            except Exception:raise ValueError('Invalid mapped rate') from None
            if not rate.is_finite() or not 0<=rate<=100:raise ValueError('Invalid mapped rate')
        return value


def load_server(ref):
    try:
        values=json.loads(os.getenv('ODOO_SERVERS_JSON','{}'))
        if ref not in values:reject('not_configured','Servidor Odoo no configurado',424)
        server=Server.model_validate(values[ref]);parts=urlsplit(server.base_url)
        if not parts.hostname or not parts.hostname.isascii() or parts.username or parts.password or parts.query or parts.fragment or parts.path not in ('','/') or not parts.hostname:raise ValueError()
        if parts.scheme!='https':
            if parts.scheme!='http' or not server.allow_insecure_test or os.getenv('ODOO_TEST_MODE')!='true':raise ValueError()
        if parts.port is not None and not 1<=parts.port<=65535:raise ValueError()
        for network in server.allowed_networks:ipaddress.ip_network(network,strict=True)
        for key,value in values.items():
            if key==ref:continue
            other=Server.model_validate(value)
            if other.base_url.rstrip('/').lower()==server.base_url.rstrip('/').lower() and other.database==server.database and (other.tenant_id!=server.tenant_id or not server.allow_multi_company or not other.allow_multi_company):
                raise ValueError()
        return server
    except Exception as exc:
        from .errors import IntegrationError
        if isinstance(exc,IntegrationError):raise
        reject('configuration','Configuración Odoo inválida',503)


def credentials(server):
    value=os.getenv(server.api_key_env,'')
    if len(value)<16:reject('not_configured','Credencial Odoo no disponible',424)
    return SecretStr(value)


def resolve_target(server,resolver=None):
    parts=urlsplit(server.base_url);host=parts.hostname
    try:
        addresses=(resolver(host,parts.port or (443 if parts.scheme=='https' else 80)) if resolver else [r[4][0] for r in socket.getaddrinfo(host,parts.port or (443 if parts.scheme=='https' else 80),type=socket.SOCK_STREAM)])
        networks=[ipaddress.ip_network(n) for n in server.allowed_networks]
        if not addresses:raise ValueError()
        valid=[]
        for address in addresses:
            ip=ipaddress.ip_address(address)
            if getattr(ip,'ipv4_mapped',None):ip=ip.ipv4_mapped
            if ip.is_unspecified or ip.is_multicast or ip.is_link_local or ip==ipaddress.ip_address('169.254.169.254') or not any(ip in n for n in networks):raise ValueError()
            if parts.scheme=='http' and not (ip.is_private or ip.is_loopback):raise ValueError()
            valid.append(str(ip))
        return sorted(set(valid))[0]
    except Exception:reject('network_policy','Destino Odoo no permitido o no resoluble',503)
