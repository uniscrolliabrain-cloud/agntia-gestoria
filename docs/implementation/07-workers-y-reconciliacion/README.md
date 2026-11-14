# GST-C07 — Workers y reconciliación

**SCAFFOLD RECOVERY / NOT_STARTED.** [Campaña delta original](../../campaigns/07-workers-y-reconciliacion.md) · [Factory](../../factory/00-README.md) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md).

## Objetivo
Cerrar delta verificable de workers y reconciliación desde código y evidencias existentes sin reimplementar capacidades válidas.

## Dependencias
GST-C06

## Tareas pendientes
- GST-C07-T01: Congelar SHA y verificar código; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C07-T02: Reconciliar evidencias históricas con HEAD; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C07-T03: Especificar delta y superficies de escritura; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C07-T04: Definir contratos y permisos con padre; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C07-T05: Diseñar pruebas positivas y negativas; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C07-T06: Recopilar evidencias y rollback; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C07-T07: Gate Codex/arquitecto y founder; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.

## Gates sin ejecutar
- GST-C07-G01: Tenant ajeno o permiso ausente bloquea acceso/efecto.
- GST-C07-G02: Fallo o estado incierto evita duplicados y permite rollback.

Rollback: Deshabilitar capacidad nueva, preservar datos/evidencias y conciliar efectos externos.

Tras Astra y reconciliación: patchsets, pruebas y handoffs por campaña. No asumir que los 92 hallazgos históricos sigan abiertos ni que el piloto esté aprobado.
