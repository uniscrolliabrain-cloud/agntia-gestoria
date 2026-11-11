# Registro de entrega del handoff del 10/11 (1 de 4)

Rama `freebuff/gestoria-autonomo`, desde `origin/verify/odoo-complete-adapter` (`b34b8ca`, PR #11). Partes 2 a 4 en `freebuff-ledger-p0-2.md`, `freebuff-ledger-p1-1.md` y `freebuff-ledger-p1-2.md`.

Ejecución: la suite completa da 84 pasan y 6 saltos (suite de Odoo real, opt-in). Se ejecutó también sobre el árbol publicado de esta rama.

Estados: PASS (dobles) = datos sintéticos, SQLite y doble del bridge, sin Odoo real; PARTIAL = parte del criterio cubierta; BLOCKED = imposible aquí (sin Docker, sin Odoo 19, sin runtime de Agente, sin workflows); NOT VERIFIED = implementación sin evidencia.

## Laboratorio y pruebas reales

| ID | Estado | Evidencia y límite |
|---|---|---|
| 01 | PASS (dobles) | `test_01_bridge_receives_invoice_ids_and_never_ids`: vista previa y relectura previa al commit envían `{company_id, invoice_ids}`, sin `ids`. Bridge real y run 42904254831 no ejecutados. |
| 02 | BLOCKED | Dos bases Odoo con volúmenes nuevos. |
| 03 | BLOCKED | `tests/integration/test_odoo_live.py` listo, se salta sin laboratorio y marcador privado. |
| 04 | PASS (dobles) | `test_04_generic_orm_writes_are_rejected_before_http`: `res.partner.write/create` y `account.move.write/action_post` se rechazan sin emitir HTTP. Guard del addon solo por lectura estática. |
| 05 | BLOCKED | Requiere PostgreSQL y filestore. |
| 06 | BLOCKED | Variante de laboratorio sin addon contable. |
| 07 | PARTIAL | Revalidación de principal y revocación de actor al ejecutar; caducidad real pendiente. |
| 08 | NOT VERIFIED | `discovery` da `evidence_hash` y versión, sin artefacto de laboratorio que registrar. |
| 09 | BLOCKED | Aprovisionamiento desde cero e interrupción controlada. |
| 10 | PARTIAL | Este registro enlaza cada punto con su evidencia; la correspondencia C02 a C20 necesita revisión del propietario. |

## Aislamiento, permisos y revisión

| ID | Estado | Evidencia y límite |
|---|---|---|
| 11 | BLOCKED | El cierre humano vive en PR #12 / `fix/human-case-closure` (`78ca93b`), fuera de esta base; portarlo exige commit trazable. El agente sigue sin clasificar ni revisar. |
| 12 | PARTIAL | `test_12_role_matrix_positive_and_negative`: lectura para los cuatro roles; proponer solo owner/reviewer/agent; aprobar y comitear solo owner/reviewer. Faltan adjuntos, exportación y conflictos. |
| 13 | PARTIAL | `test_13_second_binding_to_same_instance_needs_explicit_multi_company`: otro tenant sobre la misma instancia se rechaza siempre; hermanas exigen multiempresa explícita en ambos bindings. La prueba con dos compañías en una base necesita laboratorio. |
| 14 | PARTIAL | `test_14_shared_contact_is_rejected_instead_of_silently_imported`: `company_id` vacío da `scope_violation`. Decisión pendiente del propietario para admitirlos con regla explícita. |
| 15 | PARTIAL | `test_15_company_hierarchy_does_not_widen_the_binding`: una filial no amplía el ámbito; jerarquía real pendiente. |
| 16 | PASS (dobles) | `test_16_scope_matrix_blocks_before_http`: instancia, compañía remota, base de datos y mapeo fiscal se bloquean antes de cualquier HTTP; credencial ausente sin petición. |
| 17 | PASS (dobles) | `test_17_rotation_with_queued_job_fails_closed`: trabajo encolado pasa a `failed` con `configuration_changed`, sin llamar al proveedor. |
| 18 | PASS (dobles) | `test_18_changes_after_approval_invalidate_it`: configuración distinta, aprobación caducada y revisión de conexión distinta invalidan la aprobación (409 y 403, cero escrituras). |
| 19 | PASS (dobles + lectura estática) | La firma cubre `instance_id`, `company_id`, `operation_key`, `request_hash`, `approval_id`, `approved_by` y `expires_at`; el addon verifica HMAC, alcance, caducidad y hash. Addon real sin ejecutar. |
| 20 | PASS (dobles) | `test_20_no_sentinel_secret_reaches_public_outputs`: claves, base y credenciales ausentes en salud, capacidades, métricas, eventos, staging, conflictos, briefing, exportación y auditoría. Artefactos de CI no revisados. |
