# Registro del modulo RRHH en la aplicacion

El modulo esta implementado y probado en aislamiento. Falta el registro en `create_app`, no publicado porque `app.py` pesa 21 KB y la herramienta de publicacion rechaza ese tamano.

```python
from .integrations.rrhh.routes import register_rrhh_routes
from .integrations.rrhh.routes_closure import register_closure_routes
from .integrations.rrhh.routes_audit import register_audit_routes
...
    register_odoo_routes(app,db)
    register_rrhh_routes(app,db)
    register_closure_routes(app,db)
    register_audit_routes(app,db)
```

## Superficie publicada

| Metodo | Ruta | Que hace |
|---|---|---|
| GET | `/api/companies/{cid}/rrhh/capabilities` | Modulo encendido, zona, version de politica y capacidades |
| GET | `/api/companies/{cid}/rrhh/health` | Zona, version de politica, proveedor de nomina y ultimo snapshot |
| GET | `/api/companies/{cid}/rrhh/policy` | Politica compilada con hash y norma de cada regla |
| POST | `/api/companies/{cid}/rrhh/closures` | Prepara el cierre del periodo desde el snapshot guardado (idempotente) |
| GET | `/api/companies/{cid}/rrhh/closures/{period}` | Ultimo cierre del periodo |
| POST | `/api/companies/{cid}/rrhh/closures/{period}/approve` | Firma el cierre con motivo y aceptacion por incidencia |
| POST | `/api/companies/{cid}/rrhh/closures/{period}/export` | Manifiesto unico por cierre aprobado |
| GET | `/api/companies/{cid}/rrhh/audit` | Cadena de eventos con verificacion y punto exacto de rotura |

Ninguna de estas rutas escribe en Odoo. Preparar y exportar exigen rol `owner` o `reviewer`; aprobar exige ademas que quien preparo no sea quien firma; leer el rastro se limita a `owner` y `reviewer`.

El rastro guarda actor, accion, objeto y hashes, nunca horas de fichaje ni salarios. Un evento reescrito rompe la cadena y `audit` devuelve el numero de secuencia donde se rompe.

Las pruebas montan una `FastAPI` minima y cubren capacidades, salud, aislamiento, el flujo completo de cierre y la auditoria sin depender de `app.py`. Con el registro aplicado en local la suite completa pasa.
