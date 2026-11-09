# C02 · Auditoría upstream e imagen de referencia

Estado: **BLOCKED para cerrar el gate integral**. Auditoría estática terminada, con 38 comprobaciones ejecutadas y aprobadas. Verificación de instalación y API real: NOT VERIFIED. No avanzar a implementación de transporte ni habilitar capacidades a partir de este resultado.

Base: fusión C01 `0626ae218983337163c569bb9dc589e98775088a`. Rama: `feat/odoo-c02-upstream-audit`.

Entregables: mapa de fuentes, matriz de capacidades, licencias, UPSTREAM y lock de referencias con 22 hashes; verificador estático propio y workflow que reproduce su ejecución contra el commit fijado de Odoo. Ningún archivo original de producción o fórmula fiscal cambia. No se añade runtime, endpoint ni secreto.

```sh
python scripts/verify_odoo_source.py --source-root /ruta/a/odoo-fijado --output odoo-source-checks.json
python scripts/verify_baseline.py
```

El primer comando requiere las fuentes exactas listadas en el lock y no importa ni ejecuta Odoo. El nuevo workflow descarga esas rutas mediante checkout sparse. Un PASS estático no equivale a fields_get, search_read, permisos bot, instalación limpia, creación de draft o pruebas multiempresa.

Siguiente condición: disponer de laboratorio aislado autorizado, verificar la relación de la imagen con el SHA objetivo y ejecutar los contratos reales que exige C02. No se ha iniciado C03 como si ese gate estuviera aprobado.

## Actualizacion de relevo

El propietario solicito despues guardar todo el avance y un handoff largo en main para continuar con Codex en Windows. La PR #2 se fusiono por esa autorizacion de conservacion, en `1f8b7542d859ede4ea8b624fd3a4371ea603190e`, manteniendo BLOCKED el gate integral. Ver el handoff de la raiz; no interpretar la fusion como validacion de runtime ni permiso para futuras fusiones.
