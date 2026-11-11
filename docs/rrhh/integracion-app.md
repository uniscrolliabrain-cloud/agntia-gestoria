# Registro del modulo RRHH en la aplicacion

El modulo esta implementado y probado en aislamiento. Falta el registro en `create_app`, no publicado porque `app.py` pesa 21 KB y la herramienta de publicacion rechaza ese tamano.

```python
from .integrations.rrhh.routes import register_rrhh_routes
from .integrations.rrhh.routes_closure import register_closure_routes
...
    register_odoo_routes(app,db)
    register_rrhh_routes(app,db)
    register_closure_routes(app,db)
```

## Superficie publicada

| Metodo | Ruta | Que hace |
|---|---|---|
| GET | `/api/companies/{cid}/rrhh/capabilities` | Modulo encendido, zona, version de politica y capacidades |
| GET | `/api/companies/{cid}/rrhh/health` | Sector, proveedor de nomina y ultimo snapshot |
| GET | `/api/companies/{cid}/rrhh/policy` | Politica compilada con hash y norma de cada regla |
| POST | `/api/companies/{cid}/rrhh/closures` | Prepara el cierre del periodo desde el snapshot guardado (idempotente) |
| GET | `/api/companies/{cid}/rrhh/closures/{period}` | Ultimo cierre del periodo |
| POST | `/api/companies/{cid}/rrhh/closures/{period}/approve` | Firma el cierre con motivo y aceptacion por incidencia |
| POST | `/api/companies/{cid}/rrhh/closures/{period}/export` | Manifiesto unico por cierre aprobado |

Ninguna de estas rutas escribe en Odoo. Preparar y exportar exigen rol `owner` o `reviewer`; aprobar exige ademas que quien preparo no sea quien firma.

Las pruebas montan una `FastAPI` minima y cubren capacidades, salud, aislamiento y el flujo completo de cierre sin depender de `app.py`. Con el registro aplicado en local la suite completa pasa.
