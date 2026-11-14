# GST-C04 — Upsert y aislamiento empresas

**SCAFFOLD RECOVERY / NOT_STARTED.** [Campaña delta original](../../campaigns/04-upsert-y-aislamiento-empresas.md) · [Factory](../../factory/00-README.md) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md).

## Objetivo
Cerrar delta verificable de upsert y aislamiento empresas desde código y evidencias existentes sin reimplementar capacidades válidas.

## Dependencias
GST-C03

## Tareas pendientes
- GST-C04-T01: Congelar SHA y verificar código; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C04-T02: Reconciliar evidencias históricas con HEAD; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C04-T03: Especificar delta y superficies de escritura; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C04-T04: Definir contratos y permisos con padre; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C04-T05: Diseñar pruebas positivas y negativas; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C04-T06: Recopilar evidencias y rollback; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C04-T07: Gate Codex/arquitecto y founder; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.

## Gates sin ejecutar
- GST-C04-G01: Tenant ajeno o permiso ausente bloquea acceso/efecto.
- GST-C04-G02: Fallo o estado incierto evita duplicados y permite rollback.

Rollback: Deshabilitar capacidad nueva, preservar datos/evidencias y conciliar efectos externos.

Tras Astra y reconciliación: patchsets, pruebas y handoffs por campaña. No asumir que los 92 hallazgos históricos sigan abiertos ni que el piloto esté aprobado.
