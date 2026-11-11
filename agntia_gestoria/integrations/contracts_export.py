"""Exportación estable de los DTOs que consume Agente (tarea 55 del handoff).

Solo se publican los esquemas que un consumidor real usa hoy. El paquete y la
API validan la misma matriz: un campo nuevo necesita versión de esquema y una
regresión de compatibilidad, nunca un cambio silencioso de forma.
"""
from .contracts import (CapabilityReport,Conflict,ExternalObjectLink,ImportPreview,
                        OperationEnvelope,OperationResult,SyncJob,SyncCursor)

SCHEMA_VERSION=1
CONSUMED={
    'CapabilityReport':CapabilityReport,
    'ExternalObjectLink':ExternalObjectLink,
    'ImportPreview':ImportPreview,
    'SyncCursor':SyncCursor,
    'SyncJob':SyncJob,
    'Conflict':Conflict,
    'OperationEnvelope':OperationEnvelope,
    'OperationResult':OperationResult,
}


def export():
    return {
        'schema_version':SCHEMA_VERSION,
        'source':'agntia_gestoria.integrations.contracts',
        'mapping_version':'odoo19-v1',
        'models':{name:model.model_json_schema() for name,model in sorted(CONSUMED.items())},
    }
