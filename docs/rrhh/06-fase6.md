# Fase 6 · Hardening, operación y piloto

Objetivo: que lo construido aguante permisos cambiantes, fallos y restauración, y que exista evidencia para decidir el piloto.

## Etapa 6.1 · Permisos, aislamiento y secretos

- **Nuevos:** `tests/test_rrhh_permission_matrix.py`, `tests/test_rrhh_secrets.py`, `docs/odoo-adapter/rrhh-threat-model.md`.
- **Tocados:** `auth.py` (SEC-02, SEC-05: sesión opaca y cookie `Secure`), `app.py` (SEC-06: no devolver `str(exc)`), `integrations/rrhh/*` (revisión de trazas).
- **Reglas:** matriz actor × empresa × capacidad × superficie (API, SDK, worker); baja de permisos en mitad de una tarea bloquea antes del efecto; centinelas sintéticos en logs, trazas, exportaciones y backups.
- **Tests:** revocación en curso, token robado sin sesión válida, centinela ausente en cada salida pública, rotación de secreto sin romper datos cifrados.
- **Aceptación:** cero apariciones de centinelas y cero accesos cruzados en la matriz completa.

## Etapa 6.2 · Resiliencia, rendimiento y recuperación

- **Nuevos:** `tests/test_rrhh_resilience.py`, `tests/test_rrhh_performance.py`, `tests/test_rrhh_restore.py`, `scripts/rrhh_restore_drill.py`.
- **Tocados:** `integrations/odoo/transport.py` (cliente reutilizado, timeouts por servidor, `Retry-After`), `integrations/retention.py` (BUG-07: aplicar de verdad), `migrations.py` (BUG-13: rotación de copias).
- **Reglas:** disyuntor por proceso con sonda, trabajos huérfanos con barrido, restauración conjunta Gestoría + Odoo + adjuntos + ledger, retención de 42 días ejecutada por tarea programada.
- **Tests:** proveedor caído, latencia p50/p95 con 1.000 y 10.000 fichajes, restore completo con reconciliación posterior, purga que no borra lo vigente.
- **Aceptación:** medidas registradas con tamaño de muestra y restore cronometrado, no estimado.

## Etapa 6.3 · Observabilidad, runbooks y piloto

- **Nuevos:** `docs/odoo-adapter/rrhh-runbook.md`, `docs/odoo-adapter/rrhh-pilot-checklist.md`, `tests/test_rrhh_health.py`.
- **Tocados:** `integrations/rrhh/routes.py` (`/health` público sin credencial), `metrics.py` (etiquetas por capacidad sin secretos), `docs/odoo-adapter/RUNBOOK.md`.
- **Reglas:** logging estructurado con correlación entre repos, salud con estado de proveedor y antigüedad de snapshot, runbooks de proveedor caído, identidad errónea, credencial revocada y efecto incierto.
- **Tests:** salud sin credencial, salud con Odoo caído, alerta por trabajo huérfano, runbook validado por alguien que no escribió el código (registro firmado).
- **Aceptación:** piloto de lectura con checklist firmada, y matriz de entrega con flujo, SHA, pruebas reales y limitaciones declaradas.
