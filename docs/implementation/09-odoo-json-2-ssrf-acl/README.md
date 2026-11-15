# GST-C09 — Odoo JSON-2 SSRF ACL

**SCAFFOLD RECOVERY / NOT_STARTED.** [Campaña delta original](../../campaigns/09-odoo-json-2-ssrf-acl.md) · [Factory](../../factory/00-README.md) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md).

## Objetivo
Cerrar delta verificable de odoo json-2 ssrf acl desde código y evidencias existentes sin reimplementar capacidades válidas.

## Dependencias
GST-C08

## Tareas pendientes
- GST-C09-T01: Congelar SHA y verificar código; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C09-T02: Reconciliar evidencias históricas con HEAD; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C09-T03: Especificar delta y superficies de escritura; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C09-T04: Definir contratos y permisos con padre; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C09-T05: Diseñar pruebas positivas y negativas; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C09-T06: Recopilar evidencias y rollback; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.
- GST-C09-T07: Gate Codex/arquitecto y founder; Evidencia reproducible SHA y entorno; BLOCKED si no se ejecuta.

## Gates sin ejecutar
- GST-C09-G01: Tenant ajeno o permiso ausente bloquea acceso/efecto.
- GST-C09-G02: Fallo o estado incierto evita duplicados y permite rollback.

Rollback: Deshabilitar capacidad nueva, preservar datos/evidencias y conciliar efectos externos.

Tras Astra y reconciliación: patchsets, pruebas y handoffs por campaña. No asumir que los 92 hallazgos históricos sigan abiertos ni que el piloto esté aprobado.

## Estado ejecutado · 2026-11-14

Base `5dd9395`. Esta campaña deja de ser solo scaffold en su frontera de red y credencial.

| Tarea | Estado | Evidencia |
|---|---|---|
| GST-C09-T01 congelar SHA | PASS | `verify_baseline.py` PASS, 43 ficheros y 45 rutas |
| GST-C09-T02 reconciliar evidencias | PASS | [Auditoría 2026-11-14](../AUDIT-2026-11-14.md) |
| GST-C09-T03 delta de superficie | PASS | `registry.py`, política de red y `resolve_target` revisados |
| GST-C09-T05 pruebas negativas | PASS | `RegistryHardeningTests`, 3 tests y 9 subtests |
| GST-C09-T06 evidencias y rollback | PARTIAL | Rollback es revertir el commit; sin restore ensayado |
| GST-C09-T07 gate Codex y founder | BLOCKED | Requiere revisión humana |

Cambios: se rechazan hosts numéricos ambiguos (`2130706433`, `0x7f000001`, `017700000001`,
`127.1`, `0x7f.0.0.1`) antes de resolver, y la credencial debe cumplir `[!-~]{16,512}` para
no inyectar caracteres en la cabecera `Authorization`. El literal canónico y el nombre DNS
siguen admitiéndose.

Sigue pendiente lo que exige proveedor real: DNS controlado, resolución con `allow_networks`
en una instancia viva y verificación de que el `Host` y el SNI no permiten confusión de
autoridad.
