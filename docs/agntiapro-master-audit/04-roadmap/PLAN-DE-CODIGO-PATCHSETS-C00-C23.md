# PLAN DE CÓDIGO — MATRIZ DE PATCHSETS C00–C23

**Fuente:** inspección directa de código main y documentos existentes, 16-11-2026. Rutas de prueba son **NUEVAS PROPUESTAS**; rutas de implementación deben revalidarse en HEAD. Esta matriz complementa cada `05-campanas/Cxx-*/CAMPANA.md`. No ejecutar automáticamente efectos externos. Se proponen 24 campañas × 3 waves × 6 patchsets = 144 patchsets. Los tests aquí son objetivos, no resultados.

## Contrato universal de implementación
Cada Cxx: W1 PS01.1 inspeccionar archivos+callgraph+tests y congelar SHA; PS01.2 aprobar ADR, schema, permisos, migración aditiva, feature flag. W2 PS02.1 implementar código y wiring API→authz→dominio→persistencia→outbox; PS02.2 probar fallos, replay, concurrencia, regresión. W3 PS03.1 ejecutar unit/integration/E2E/security/contract tests, medir performance, rollback; PS03.2 registrar EXECUTION-REPORT, SHA, pruebas, divergencias, PR y handoff. Un PASS solo con evidencia; skip obligatorio = BLOCKED. Todos los nuevos ficheros y dependencias se justifican antes de escribir.

## Tabla operativa por campaña

| Campaña | Archivos existentes para inspeccionar/modificar (verificar) | Código y wiring exactos | Test NUEVO propuesto | Gate de aceptación |
|---|---|---|---|---|
| C00 | `scripts/verify_baseline.py`, `pyproject.toml`, `.github/workflows/` | inventario reproducible, hashes, rutas y test matrix | `tests/test_baseline.py` | C00 inventory SHA, branch provenance y baseline CI |
| C01 | `docs/product-scope.md`, `agntia_gestoria/app.py`, `agntia_gestoria/tax.py`, `integrations/rrhh/` | manifest de capacidades por estado y proveedor, sin declarar cumplimiento | `tests/test_capability_manifest.py` | JSON manifest v1 + prueba contra rutas reales |
| C02 | `agntia_gestoria/auth.py`, `agntia_gestoria/integrations/registry.py`, `agntia_gestoria/integrations/odoo/transport.py` | threat model, auth negative tests, SSRF and secret redaction | `tests/test_security_boundaries.py` | IDOR/SSRF/replay/secret leak suite |
| C03 | `agntia_gestoria/auth.py`, `agntia_gestoria/sessions.py`, `agntia_gestoria/integrations/policy.py` | nuevo adapter identity delegation; tenant-company binding; revocation | `tests/test_delegated_identity.py` | actor canónico verificado sin owner impersonation |
| C04 | `integrations/agente/src/index.ts`, `agntia_gestoria/integrations/policy.py` | separar readOnlyTools/proposalTools y capability allowlist | `integrations/agente/src/tools.test.ts` | 0 herramientas mutates en catálogo read-only |
| C05 | `integrations/agente/src/index.ts`, `typescript/index.ts`, `typescript/odoo.ts` | schema v1, errores top-level/detail, client TS, compat y URI encoding | `integrations/agente/src/contracts.test.ts` | contract tests SDK/API 401/403/409/422/503 |
| C06 | `infra/odoo/lab.sh`, `infra/odoo/compose.standalone-lab.yaml`, `infra/odoo/smoke.py` | lab Odoo 19 real, dos DB, ACL, addons y variante sin account | `tests/test_odoo_live_lab.py` | smoke live + digest imagen + restore |
| C07 | `agntia_gestoria/integrations/odoo/service.py`, `agntia_gestoria/integrations/registry.py` | tenant binding, instance identity, remote company y ACL | `tests/test_odoo_acl_live.py` | denegación cross-company en Odoo live |
| C08 | `agntia_gestoria/integrations/odoo/imports.py`, `agntia_gestoria/integrations/odoo/jobs.py` | preview→staging→unverified con dedup y provenance | `tests/test_odoo_import_idempotency.py` | replay sin duplicados ni clasificación automática |
| C09 | `agntia_gestoria/integrations/odoo/commands.py`, `infra/odoo/addons/agntia_bridge/models/bridge.py` | approval hash, ledger, unknown-commit y reconcile | `tests/test_odoo_commit_reconcile.py` | una escritura remota por operation key |
| C10 | `agntia_gestoria/integrations/odoo/jobs.py`, `agntia_gestoria/integrations/migrations.py` | lease, crash, restart, retry budget, pending/DLQ | `tests/test_odoo_worker_recovery.py` | concurrencia y recuperación sin doble efecto |
| C11 | `agntia_gestoria/storage.py`, `agntia_gestoria/app.py` | originales hash, acceso, antivirus hook, retención, auditoría | `tests/test_document_evidence.py` | evidence chain con rechazo cross-company |
| C12 | `agntia_gestoria/tax.py`, `agntia_gestoria/storage.py` | fingerprint, revisión, invalidación stale y bloqueo | `tests/test_stale_review.py` | snapshot obsoleto no autorizable |
| C13 | `agntia_gestoria/engines.py`, `agntia_gestoria/rules.py`, `agntia_gestoria/tax.py` | golden 303 2026 common scope, Decimal y unsupported | `tests/test_303_golden.py` | fixtures oficiales revisados por profesional |
| C14 | `agntia_gestoria/engines.py`, `agntia_gestoria/rules.py`, `agntia_gestoria/tax.py` | golden 130 2026 scope, exclusions, rounding | `tests/test_130_golden.py` | fixtures oficiales revisados por profesional |
| C15 | `agntia_gestoria/rules.py`, `agntia_gestoria/data/`, `docs/legal-research.md` | calendario y jurisdicción versionados, provenance legal | `tests/test_obligation_calendar.py` | no auto-activation of unverified legal rule |
| C16 | `agntia_gestoria/storage.py`, `agntia_gestoria/tax.py` | journal drafts, double-entry validation, reconciled exceptions | `tests/test_accounting_drafts.py` | no external posting and balanced drafts |
| C17 | `agntia_gestoria/integrations/registry.py`, `agntia_gestoria/integrations/policy.py` | read-only PSD2 adapter isolated with consent and revoke | `tests/test_banking_readonly.py` | no payment capability, revocation effective |
| C18 | `agntia_gestoria/integrations/odoo/evidence.py`, `agntia_gestoria/integrations/migrations.py` | outbox with monotonic sequence, cursor, telemetry | `tests/test_outbox_cursor.py` | no cross-tenant cursor, replay safe |
| C19 | `agntia_gestoria/storage.py`, `infra/odoo/lab.sh`, `scripts/` | backup consistent SQLite WAL + originals + Odoo PG/filestore | `tests/test_backup_restore.py` | restore test with measured RTO/RPO |
| C20 | `agntia_gestoria/static/`, `agntia_gestoria/report_routes.py`, `typescript/` | human workspace evidence/approval states, no fake progress | `tests/test_workspace_accessibility.py` | browser E2E and role isolation |
| C21 | `agntia_gestoria/integrations/odoo/commands.py`, `integrations/agente/src/index.ts` | approval bridge to Agente canonical authority, hash/expiry/revoke | `tests/test_agente_approval_contract.py` | no commit without fresh verified human approval |
| C22 | `scripts/simulation/run.py`, `infra/odoo/`, `tests/` | 2 synthetic tenants, 2 DB, auth, event, recovery, real E2E | `tests/test_two_tenant_e2e.py` | no cross-tenant data/effects |
| C23 | `.github/workflows/`, `docs/odoo-adapter/pilot-acceptance.md`, `docs/agente-integration.md` | release matrix, SBOM, contract fixtures, risk register and go/no-go | `tests/test_release_gates.py` | no skipped required tests and founder approval |

## Matriz de dependencias de código
C00→C01→C02→C03→C04→C05. C05→C06→C07→C08→C09→C10. C03→C11→C12→C13/C14→C15/C16. C03+C05→C17. C09+C10→C18→C19. C05+C12→C20. C03+C05+C09→C21. C06+C07+C09+C10+C18+C19+C21→C22→C23. C17 puede bloquearse por proveedor sin bloquear certificación del scope MVP que lo excluya explícitamente.

## Baseline técnico observado
`storage.py`: SQLite WAL, `BEGIN IMMEDIATE`, `companies/objects/audit`, hash chain. `integrations/migrations.py`: DDL aditiva v1 con `provider_connections`, `external_links`, `integration_staging`, `sync_jobs`, `integration_outbox`, `idempotency_keys`, `integration_proposals`, `integration_approvals`. `jobs.py`: lease de 10 min, heartbeat, presupuesto 3 intentos, estado `reconciliation_required`; no reescribir sin test de crash. `policy.py`: READ/PROPOSE/HUMAN, ODOO_IDENTITY_MODE standalone/integrated, actor scopes. `commands.py`: propuestas con TTL 15 min, hash, aprobaciones, operación idempotente; bridge Odoo HMAC. `tax.py`: registro unverified/reviewed, fingerprint, 303/130 acotados. Estos hechos NO acreditan live E2E.

## Comandos de verificación sugeridos
```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m unittest discover -s tests
npm --prefix integrations/agente install
npm --prefix integrations/agente run typecheck
npm --prefix integrations/agente run build
bash -n infra/odoo/lab.sh
docker compose -f infra/odoo/compose.standalone-lab.yaml config
```
Confirmar la presencia y compatibilidad de scripts y dependencias antes de ejecutarlos. No instalar ni iniciar Odoo en entorno productivo. Si no hay Docker, dejar live tests BLOCKED. No afirmar 0 fallos sin ejecutar.

## Criterios de modificación
No reemplazar `Database`, `Adapter`, `Commands`, `Jobs`, `Client` ni `policy` por capas paralelas. Preferir mejoras incrementales, módulos nuevos solo para adaptadores/versionado, migraciones aditivas y test de rollback. Prohibido mezclar cambios de otros 13 repos sin contrato versionado. No hacer merge a main, ni despliegue, ni presentación fiscal, ni pagos.
