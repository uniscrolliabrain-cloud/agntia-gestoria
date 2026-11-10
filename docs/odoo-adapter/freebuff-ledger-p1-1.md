# Registro de entrega del handoff del 10/11 (3 de 4)

Continuación de `freebuff-ledger-p0-2.md`.

## Importación y calidad de datos

| ID | Estado | Evidencia y límite |
|---|---|---|
| 40 | PASS (dobles) | `test_more_than_thousand_partners_keyset_pagination`: 1101 contactos sin pérdida ni duplicación. |
| 41 | PASS (dobles) | `test_41_identical_write_dates_resume_without_loss`: 250 objetos con el mismo `write_date` en orden por id. |
| 42 | PASS (dobles) | `test_preview_source_change_blocks_acceptance`: cambio remoto entre vista previa e importación da 409. |
| 43 | PARTIAL | El replay concurrente crea un solo hecho; no se inyectó fallo a mitad de guardado ni tras el commit. |
| 44 | PARTIAL | `remote_missing` genera conflicto y marcador sin borrar historial; la matriz archivado, borrado y acceso perdido necesita laboratorio. |
| 45 | PASS (dobles) | `test_45_ambiguous_identities_are_not_deduplicated`: mismo NIF e ids distintos producen dos objetos. |
| 46 | PARTIAL | Fixtures de redondeo, abono y moneda extranjera bloqueada; rectificativas, descuentos e impuestos compuestos pendientes. |
| 47 | PARTIAL | Líneas informativas separadas y técnicas no soportadas bloquean el mapeo; faltan vencimientos y redondeos. |
| 48 | PASS (dobles) | `test_mapping_rounding_refund_and_ambiguity`: base, impuestos y total reconciliados con precisión decimal. |
| 49 | PASS (dobles) | `test_mapping_blocked_and_source_conflict_stales_calculation`: la revisión se conserva y el cambio de origen abre conflicto. |
| 50 | BLOCKED | Vista de operador: trabajo de interfaz. |
| 51 | PASS (dobles) | `test_51_partial_batch_reports_blocked_and_imported`: lote mixto informa `mapping_blocked` e `imported` por separado. |
| 52 | PARTIAL | Documento cifrado, nombre saneado, descarga autorizada y escáner obligatorio; rotación y restauración necesitan laboratorio. |

## Contratos, eventos y experiencia

| ID | Estado | Evidencia y límite |
|---|---|---|
| 53 | PARTIAL | Se reutiliza el outbox `schemaVersion: 1`; cualquier extensión debería versionarse. Falta ADR del propietario. |
| 54 | PARTIAL | Acuse idempotente por consumidor y detección de manipulación; cursor expirado, reentrega y dos empresas necesitan laboratorio. |
| 55 | PARTIAL | `docs/odoo-adapter/schemas/contracts-v1.json` lo genera `scripts/export_contract_schemas.py` y un test detecta deriva. Falta validar los ejemplos TypeScript. |
| 56 | PASS (dobles) | `test_56_every_emitted_error_code_has_a_contract` recorre el código y exige categoría y acción siguiente; un código futuro cae en `integration` sin filtrar detalles. |
| 57 | PASS (dobles) | `test_57_capabilities_expose_freshness_and_provenance`: `checked_at`, `expires_at` y `stale`; publicación remota y presentación oficial en falso. |
| 58 | BLOCKED | Vista de datos reales: interfaz. |
| 59 | BLOCKED | Decisión de producto sobre cuándo Laia muestra una vista. |
| 60 | BLOCKED | Enlaces de afirmaciones a evidencia: interfaz. |
| 61 | PARTIAL | El conflicto abre marcador de ajuste y conserva el original; `data_changed_since_calculation` solo se comprueba en la suite real. |
| 62 | PARTIAL | Los motores fiscales viven en Gestoría y el adaptador no los duplica; revisar el consumidor exige el SDK de Agente. |
