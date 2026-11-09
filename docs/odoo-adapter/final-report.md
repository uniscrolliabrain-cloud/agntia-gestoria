# Informe al founder · implementación Odoo completa para laboratorio

Fecha: 2026-11-09. Base main: `1fd25d932a26acab0d865aa4aa3d7ed83876282e`. Rama: `feat/odoo-complete-adapter`. El código de C03–C20 se entrega por lote por orden del propietario; esta entrega no certifica Odoo real, no aplica cambios en agente y no despliega producción.

## Estado por campaña

| Campaña | Estado de gate | Implementación/evidencia |
|---|---|---|
| C01 | PASS | Baseline histórico PR1, 43 fuentes conservadas con política explícita de8 cambios autorizados por alcance; hashes antiguos/nuevos exactos |
| C02 | BLOCKED | Auditoría estática PR2, upstream fijado; gate de instancia sigue sin ejecutar |
| C03 | NOT VERIFIED | Laboratorio Docker/digests/fuente fijada y provisión de dos DB; no arrancado |
| C04 | PASS | Contratos locales cerrados, esquema/round-trip/Decimal y validación; no acredita proveedor |
| C05 | NOT VERIFIED | Migración fresh/upgrade/no-op/rollback/backup locales probados; restore WAL operativo pendiente |
| C06 | NOT VERIFIED | Registro/scopes/SSRF/secretos implementados y simulados; rotación/TLS reales pendientes |
| C07 | NOT VERIFIED | Transporte probado con MockTransport; JSON-2 real pendiente |
| C08 | NOT VERIFIED | Discovery fail-closed simulado; módulos/ACL reales pendientes |
| C09 | NOT VERIFIED | Binding/revocación/cross-company simulados; dos DB reales pendientes |
| C10 | NOT VERIFIED | Contactos y 1101 elementos simulados; proveedor real pendiente |
| C11 | NOT VERIFIED | Snapshots/reconciliación y bloqueos implementados; matriz fiscal real pendiente |
| C12 | NOT VERIFIED | Staging/import unverified/replay/frescura probados localmente; lotes reales pendientes |
| C13 | NOT VERIFIED | Cursos/leases/retries/conflictos/recovery implementados; crashes reales pendientes |
| C14 | NOT VERIFIED | Originales cifrados/scanner/límites probados con fixture; scanner y custodia real pendientes |
| C15 | NOT VERIFIED | Propuesta/aprobación/firma/idempotencia/contactos; write-back real pendiente |
| C16 | NOT VERIFIED | Factura borrador/reconciliación/bloqueos; creación ORM real pendiente |
| C17 | NOT VERIFIED | Dos addons propios necesarios; instalación/concurrencia/ACL real pendientes |
| C18 | NOT VERIFIED | API/SDK/Hono y contratos locales; integración Hono/browser actual pendientes |
| C19 | NOT VERIFIED | Tools/eventos/ACK/briefing implementados; wiring AgntiaPro no autorizado/aplicado |
| C20 | NOT VERIFIED | Pruebas locales y recetas E2E/backup/CI entregadas; aceptación real pendiente |

## Pruebas y entrega

Ver [c20/local-results.json](c20/local-results.json) para número exacto ejecutado/pasado/fallido, duración y versiones. Tests Python locales usan un workaround del selector de este sandbox; CI estándar PASS sobre el código `84504053d71c966db58d8de0fdf44b9817ebef82`: 57/57 sin workaround, 4/4 Node y navegador desktop/móvil, descarga de informe y creación de registro. Evidencia: [c20/ci-results.json](c20/ci-results.json). Node build/sintaxis y un archivo de pruebas Node pasan. Docker, backup real y E2E Odoo real siguen NOT VERIFIED. El navegador de la UI existente sí aprobó en CI; no es un test de una nueva UI ERP. No se han usado datos de clientes.

Historial remoto previo: PR1 merge `0626ae218983337163c569bb9dc589e98775088a`; PR2 merge `1f8b7542d859ede4ea8b624fd3a4371ea603190e`; handoff main `1fd25d932a26acab0d865aa4aa3d7ed83876282e`. Código entregado en `84504053d71c966db58d8de0fdf44b9817ebef82`, PR [#4](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4); actualización documental posterior con resultados CI. No se inventan20 PR independientes.

## Capacidades reales y límites

El sistema puede configurar un binding, diagnosticar, previsualizar/importar, conservar origen/documentos, detectar conflictos, proponer/aprobar y proyectar contactos/borradores con bridge. La prueba local verifica estas rutas con proveedor sintético. Las capacidades de una instancia concreta solo se habilitan al validar discovery y caducan en1h. Leer [COMPATIBILITY.md](COMPATIBILITY.md), [contracts.md](contracts.md) y la matriz histórica de fuente. No instalar OCA indiscriminadamente ni asumir cobertura territorial por l10n_es.

Prohibido: publicar/postear, enviar facturas, borrar movimientos, pagos/conciliación bancaria, nóminas/presentación fiscal. Cero llamadas a action_post en el adaptador y en los tests; guardas del addon deben probarse en entorno real. Cero importados auto-reviewed en tests. No hay scheduler empresarial, coste inventado ni actividad simulada presentada como real.

## Coste y riesgos

Coste de proveedor por llamada Community: no se ha medido tarifa/infraestructura. Hipótesis de laboratorio: 6–8GB RAM host y almacenamiento suficiente para fuente/imágenes/Postgres/filestore/backups; medir CPU/RAM/IO y p50/p95 bajo carga real. No se fija coste mensual sin conocer hosting, región, retención y número de tenants. Métricas API reflejan solo llamadas observadas, no coste total.

Pendientes materiales: build del SHA contra base, compatibilidad del addon ORM/ACL19, carreras de PostgreSQL, restauración/cifrados/claves, revisión humana/fiscal competente, scanner/TLS/RGPD y prueba del consumidor Hono. SQLite continúa limitado a despliegue inicial. La firma confía en el servidor aprobador y las credenciales humanas; no equivale a MFA ni presencia física certificada. Auditoría local no sustituye anclaje externo contra administrador comprometido.

## Próximos pasos autorizados y aprobación

La otra IA puede usar [RUNBOOK.md](RUNBOOK.md) para instalar/testear Docker sintético, corregir fallos y registrar resultados sin datos reales. Revisar [pilot-acceptance.md](pilot-acceptance.md). Producción, wiring en `agente` y ampliación fiscal requieren las aprobaciones expresas de la campaña original; no se solicitan como obstáculo para entregar el código de laboratorio. Rollback: flag off/reiniciar, conservar links/evidencias, conciliar sin borrar movimientos.
