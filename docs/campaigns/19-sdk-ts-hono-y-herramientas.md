# GST-C19 — SDK TS/Hono y herramientas

**RECOVERY_DELTA / PLANNED / NOT_EXECUTED.** Cerrar delta verificable de sdk ts/hono y herramientas desde código y evidencias existentes sin reimplementar capacidades válidas.

Fuentes: `README.md`, `docs/odoo-adapter/CAMPAIGN.md`, `docs/odoo-adapter/freebuff-operational-2026-11-11.md`, `docs/odoo-adapter/pilot-acceptance.md`. Dependencias: GST-C18. [Factory](../factory/00-README.md), [flow](../factory/01-PIPELINE.md), [baseline](../prep/README.md).

## Tareas previstas
- GST-C19-T01: Congelar SHA y verificar código. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C19-T02: Reconciliar evidencias históricas con HEAD. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C19-T03: Especificar delta y superficies de escritura. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C19-T04: Definir contratos y permisos con padre. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C19-T05: Diseñar pruebas positivas y negativas. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C19-T06: Recopilar evidencias y rollback. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C19-T07: Gate Codex/arquitecto y founder. Aceptación: Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.

## Gates no ejecutados
- GST-C19-G01: Tenant ajeno o permiso ausente bloquea acceso/efecto.
- GST-C19-G02: Fallo o estado incierto evita duplicados y permite rollback.

Rollback: Deshabilitar capacidad nueva, preservar datos/evidencias y conciliar efectos externos.

Tras meta-auditoría libre Astra y reconciliación: concretar patchsets, ownership, pruebas y handoffs por campaña. Auditoría de 92 hallazgos histórica; verificar fixes en HEAD, no tratarlos automáticamente como abiertos.
