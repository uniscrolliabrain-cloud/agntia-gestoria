# Registro de entrega del handoff del 10/11 (4 de 4)

Continuación de `freebuff-ledger-p1-1.md`, con el cierre de la entrega.

## Operación, recuperación y piloto

| ID | Estado | Evidencia y límite |
|---|---|---|
| 63 | BLOCKED | Cargas con p50 y p95: requiere laboratorio. |
| 64 | PASS (dobles) | `test_64_metrics_are_labelled_per_capability_without_secrets`: `/metrics` añade `by_operation` con p50, p95 y fallos, sin secretos. |
| 65 | PARTIAL | La degradación de conexión se registra y se refleja en salud; enrutado de alertas y umbrales necesitan operación real. |
| 66 | PARTIAL | WAL, `BEGIN IMMEDIATE` y rollback de migración cubiertos; dos procesos no se han probado. |
| 67 | BLOCKED | Restauración del conjunto completo. |
| 68 | PARTIAL | Desactivación por conexión y ámbito por tenant impiden nuevas ejecuciones; falta ensayar operaciones pendientes. |
| 69 | PARTIAL | Existe `docs/odoo-adapter/RUNBOOK.md`; esta entrega añade el criterio de resultado incierto. Faltan simulacros. |
| 70 | BLOCKED | Piloto de lectura: decisión y checklist del propietario. |
| 71 | PARTIAL | Proyección de borrador con totales verificados y un solo efecto remoto; el contacto aprobado real necesita laboratorio. |

## Evolución del producto

Todos pendientes de decisión de producto: 72 compras y proveedores, 73 justificantes, 74 bandeja de revisión, 75 informes de gestión, 76 versionado de reglas, 77 fiscalidad por bloques, 78 localizaciones y addons, 79 preparación, emisión y presentación, 80 banca y conciliación, 81 conservación y baja, 82 demo repetible. Primer paso en `pendientes.md`.

## 83 · Entrega para la revisión del 11 de noviembre

- Rama `freebuff/gestoria-autonomo` sobre `b34b8ca`.
- Código nuevo: contrato estable de errores, exportación versionada de DTOs con test de deriva, retención del ledger y métricas por capacidad. Regresiones nuevas: 26 casos en `tests/test_freebuff_backlog.py`.
- Probado con dobles: 01, 04, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 36, 40, 41, 42, 45, 48, 49, 51, 55 (Python), 56, 57 y 64.
- Probado con Odoo real: nada. Ningún run de CI abierto.
- Cambios de contrato: `public()` añade `category` y `next_action`; `/metrics` añade `by_operation`; nuevo fichero de esquemas. Sin migraciones, sin cambios de permisos y sin tocar `app.py` ni los motores fiscales.
- Primer fallo reproducible pendiente: punto 03. `AGNTIA_RUN_ODOO_TESTS=1 python -m pytest tests/integration -q` con laboratorio; sin laboratorio devuelve 6 saltos, no un PASS.
- Decisiones que necesitan revisión: contactos compartidos (14), correspondencia C02 a C20 (10), contrato de eventos (53), portar el cierre humano de PR #12 (11) y cualquier habilitación de escrituras (28).
