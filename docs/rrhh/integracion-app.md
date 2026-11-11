# Registro del modulo RRHH en la aplicacion

El modulo esta implementado y probado en aislamiento. Falta el registro en `create_app`, no publicado porque `app.py` pesa 21 KB y la herramienta de publicacion rechaza ese tamano.

```python
from .integrations.rrhh.routes import register_rrhh_routes
...
    register_odoo_routes(app,db)
    register_rrhh_routes(app,db)
```

Las pruebas montan una `FastAPI` minima y cubren capacidades, salud y aislamiento sin depender de `app.py`. Con el registro aplicado en local la suite completa pasa.
