# Registro de entrega del handoff del 10/11 (2 de 4)

Continuación de `freebuff-ledger-p0-1.md`. Mismos estados: PASS (dobles), PARTIAL, BLOCKED y NOT VERIFIED.

## Escrituras y recuperación de incertidumbre

| ID | Estado | Evidencia y límite |
|---|---|---|
| 21 | PASS (dobles) | `test_21_timeout_before_commit_keeps_result_unknown`: timeout antes del efecto deja `reconciliation_required`; el ledger vacío no se lee como ausencia comprobada y no se reintenta. |
| 22 | PASS (dobles) | `test_22_lost_ack_after_commit_reconciles_one_effect`: ACK perdido tras el efecto da reconciliación con la misma clave y un solo objeto remoto. |
| 23 | PASS (dobles) | `test_23_concurrent_same_key_yields_one_remote_operation`: dos commits simultáneos con la misma clave producen una escritura remota y un resultado común. |
| 24 | PASS (dobles) | `test_24_same_key_with_other_content_is_a_stable_conflict` (409 `idempotency_conflict`) y `test_new_key_cannot_execute_same_proposal_twice`. |
| 25 | PASS (dobles) | `test_25_restart_between_remote_effect_and_local_record`: se pierde el registro local, el reinicio reconcilia y no duplica. Reinicio simulado. |
| 26 | PASS (dobles) | `test_26_absent_ledger_and_permission_error_are_distinct`: ausencia observada no es igual a error de permisos; el estado incierto se conserva sin escrituras. |
| 27 | PASS (dobles) | `retention.py`: ventana de 42 días (reintentos 1, retrasados 7, restauración 35, margen 7); clave caducada pasa a revisión manual. |
| 28 | BLOCKED | Requiere runtime de Agente y su harness. Escrituras de Agente deshabilitadas. |

## Simulación e incorporación

| ID | Estado | Evidencia y límite |
|---|---|---|
| 29 | NOT VERIFIED | Empaquetar el SDK y consumirlo con las versiones del host. |
| 30 | BLOCKED | Lectura de extremo a extremo con Gestoría, Odoo real y runtime desechable. |
| 31 | PARTIAL | Identidad y binding se resuelven en servidor y el tenant integrado lo impone el servidor; falta la sesión autenticada real. |
| 32 | BLOCKED | Dos tenants en paralelo sobre el runtime. |
| 33 | BLOCKED | Catálogo de herramientas del runtime de Agente. |
| 34 | BLOCKED | Simulación de Gestoría caída. |
| 35 | PARTIAL | Los fallos de proveedor se tipan y no se confunden con respuesta vacía; falta el corte real de Odoo. |
| 36 | PASS (dobles) | Timeout, redirección y respuesta excesiva fallan de forma tipada, sin eco del cuerpo y sin reintentar escrituras. Sin presupuesto de latencia medido. |
| 37 | PARTIAL | Propuesta, aprobación humana sintética y ejecución autorizada con trazas de actor, hash, clave y efecto; falta el actor humano real. |
| 38 | BLOCKED | Pérdida de ACK con bridge real. |
| 39 | BLOCKED | Incorporación mínima: decisión del propietario y versión fijada. |
