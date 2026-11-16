# FREEBUFF CLOUD — HANDOFF MAESTRO DE IMPLEMENTACIÓN C00–C23

**Actualizado:** 2026-11-16. **Repositorio:** https://github.com/uniscrolliabrain-cloud/agntia-gestoria. **Rama documental:** `docs/master-audit-campaigns-20261116`. **Objetivo:** desarrollar el código de las 24 campañas documentadas, sin merge a main ni despliegue. Este handoff sustituye a la versión corta previa.

## 1. Misión ejecutiva
Eres el agente implementador principal. El fundador solicita convertir el Concept Master en un middleware Gestoría real, robusto, seguro, autónomo e integrable con `uniscrolliabrain-cloud/agente`. NO te limites a auditar, comentar, generar índices o escribir planes: **implementa código y tests campaña a campaña**, haz commits verificables, registra los reportes y continúa. Si una campaña depende de autorización humana, proveedor regulado, infraestructura o datos reales inaccesibles, márcala BLOCKED con causa y avanza a una independiente. Nunca declares un gate PASS con tests skipped ni inventes resultados.

## 2. Arranque obligatorio
```bash
git clone https://github.com/uniscrolliabrain-cloud/agntia-gestoria.git
cd agntia-gestoria
git fetch --all --prune
git checkout docs/master-audit-campaigns-20261116
git pull --ff-only origin docs/master-audit-campaigns-20261116
git rev-parse HEAD
git status --short
git switch -c feat/freebuff-gestoria-implementation-20261116
python -m pip install -e '.[dev]'
python -m pytest -q
```
Si la rama de implementación ya existe, inspecciona sus commits y continúa allí sin pisar trabajo ajeno. Los comandos requieren acceso y entorno; registra error en vez de fingir. Compara HEAD de main y la rama documental, registra SHA. No cambies main.

## 3. Biblioteca de instrucciones: orden de lectura
1. `docs/agntiapro-master-audit/README.md` y `00-estado-actual/BASELINE.md`.
2. `00-estado-actual/CALLGRAPH-VERIFICADO.md`, `HALLAZGOS-CODIGO-P2.md`.
3. `04-roadmap/PLAN-DE-CODIGO-PATCHSETS-C00-C23.md` — **matriz concreta de código de las 24 campañas, archivos existentes, tests nuevos y gates**.
4. `04-roadmap/REPLANIFICACION-P2.md`, `ORDEN-DE-EJECUCION.md`.
5. `03-integracion-agente/CONTRATOS.md` y `COMPATIBILIDAD-CODIGO-REAL.md`.
6. `docs/concept-master/CONCEPT-MASTER.md` (G01–G78 son TARGET, no implementado), `docs/CONCEPT-MASTER-AGNTIA-GESTORIA-V1.md`, `docs/odoo-adapter/pilot-acceptance.md`.
7. **Cada** `docs/agntiapro-master-audit/05-campanas/Cxx-*/CAMPANA.md` y su `EXECUTION-REPORT.md` antes de editar.

## 4. Regla de ejecución sin detenerse
Para cada C00–C23: W1/PS01.1 inventario de código real, ramas y tests; W1/PS01.2 ADR, contrato y migraciones; W2/PS02.1 implementación real; W2/PS02.2 fallos y tests negativos; W3/PS03.1 E2E, seguridad, regresión, rollback; W3/PS03.2 reporte y handoff. No omitas una wave. Commitea por patchset o bloque atómico; añade tests nuevos en la misma rama. Antes de cada patchset comprueba precondiciones y rutas existentes, instala solo deps necesarias justificadas y verifica licencia/versión. Evita reescribir implementaciones maduras o fusionar ramas archivadas automáticamente.

## 5. Primeras tareas prioritarias y rutas verificadas
**C00:** Baseline de `pyproject.toml`, `agntia_gestoria/storage.py`, `agntia_gestoria/integrations/migrations.py`, `jobs.py`, `commands.py`, `service.py`, `policy.py`, `auth.py`, `typescript/`, `integrations/agente/`, `infra/odoo/`; confirmar SHA, tests y PR. Crear inventario de test matrix y manifiesto de capacidades. 

**C02–C03:** `auth.py` usa tokens locales y sesiones; `policy.py` ya distingue READ/PROPOSE/HUMAN y standalone/integrated. No crear un segundo sistema de autoridad. Crear adaptador de delegación de Agente con claims verificados server-side, tenant binding, revocación y tests de cross-tenant. Desactivar local owner en producción y probar el rechazo.

**C04:** `integrations/agente/src/index.ts` declara `readOnlyTools` pero incluye `rrhh.closure.prepare` con `mutates:true`. Separar catálogos y probar que ningún descriptor de lectura muta; examinar consumidor y no romperlo sin compatibilidad.

**C05:** El SDK `integrations/agente/src/index.ts` interpreta `body.detail`, mientras `agntia_gestoria/integrations/odoo/routes.py` produce errores `{code,message}` top-level. Corregir compatibilidad y probar 401/403/404/409/422/503 y payload malformado. Versionar contrato sin modificar archivos internos de Agente.

**C06–C10:** Reutilizar `Adapter(Service,Imports,Jobs,Commands,Attachments)`. `storage.py` tiene WAL/BEGIN IMMEDIATE; `migrations.py` contiene `provider_connections`, `sync_jobs`, `idempotency_keys`, `integration_outbox`; `jobs.py` tiene lease+heartbeat+retry; `commands.py` propone/aprueba/commitea y `bridge.py` firma/verifica. No duplicar ledger. Validar Odoo 19 real, dos DB, ACL, timeouts pre/postcommit, reconciliación, crash/restart, recuperación y backup. `transport.py` solo reintenta lecturas y no escrituras: preservar esta propiedad.

**C11–C16:** Documentos, evidencia, revisión humana y stale invalidation; `tax.py` registra hechos unverified/reviewed, fingerprint y cálculo acotado. Golden cases de 303/130 para scope declarado 2026, no presentación fiscal. Versionar reglas y jurisdicción; cualquier ampliación fiscal exige fuentes oficiales por ejercicio y revisión profesional.

**C17:** Banca read-only con proveedor PSD2 autorizado y consentimiento; sin credenciales reales o proveedor aprobado, dejar bloqueado y seguir.

**C18–C21:** Outbox y observabilidad, backup/restore real, workspace humano y approval bridge con autoridad canónica Agente. No atribuir a un agente aprobación humana. Mantener compatibilidad con V2 mediante adaptadores versionados.

**C22–C23:** E2E dos empresas sintéticas y dos Odoo DB, certificación reproducible, matrices de aceptación, release go/no-go del fundador. Ningún despliegue automático.

## 6. Política de ingeniería innegociable
- `LLM propone, sistema dispone`; Agente gobierna identidad, policy, SOP, approval, bus. Gestoría gobierna cálculos, expedientes y evidencia. Odoo gobierna entidades ERP.
- Deny-by-default, fail-closed, least privilege, aislamiento por tenant y empresa, scopes comprobados en servidor, actor revocado denegado, idempotencyKey y hash de payload, correlación y causación.
- Toda escritura externa requiere aprobación humana fresca, vinculada al hash y a empresa, revalidada antes de ejecutar. Prohibidos pagos, emisión/publicación fiscal, envío de declaraciones o cambios de producción.
- No registrar secretos, tokens, PII ni documentos originales en logs/PR. No inventar credenciales ni usar datos reales sin autorización.
- Un `SKIP` en prueba obligatoria significa `BLOCKED`, no `PASS`. Guardar evidencia de comando, SHA, entorno, resultado, fixture y logs sanitizados.
- Cambios en DB solo mediante migraciones aditivas y backup; rollback probado, nunca eliminar ledger de operaciones ambiguas.

## 7. Contratos de AgntiaPro (propuestos; validar antes de implementar)
Solicitud de capacidad v1: `{schemaVersion, tenantId, companyId, actorId, capabilityId, correlationId, causationId, idempotencyKey, approvalRef?, payload}`. La identidad y autoridad no se confían a esos campos: la capa servidor verifica credencial de servicio, issuer, audience, expiración, scopes, tenant/company y delegación humana. Respuesta: `{jobId,status,evidenceRefs,revision,error?}`. Evento append-only: `{eventId,schemaVersion,type,source,tenantId,companyId,correlationId,causationId,sequence,occurredAt,evidenceRefs}`. No importar internals del runtime; implementar cliente y contract tests aislados.

## 8. Reportes y commits
Tras cada campaña actualiza **su** `EXECUTION-REPORT.md`: fecha, rama, SHAs antes/después, patchsets, archivos nuevos/modificados/legacy, dependencias y licencias, tests PASS/FAIL/SKIP con comandos, errores y fixes, divergencias, decisiones, riesgos, evidencia, rollback, bloqueos y handoff a la siguiente. Si el plan no encaja con el código, actualiza primero la campaña con evidencia y continúa. Commits atómicos, PR sin merge. No alteres documentación histórica para simular que una capacidad está implementada.

## 9. Condiciones de parada
Solo detener una acción que requiera aprobación/secret/proveedor, ponga en riesgo datos o producción, o cuyo gate de seguridad no pueda resolverse. Documenta el bloqueo y continúa en una campaña independiente. Solicitar fundador para elección proveedor PSD2, revisión profesional fiscal, infraestructura/credenciales de Odoo real, compatibilidad aprobada de Agente, y aprobación de merge/deploy. No detenerse tras índice, roadmap o primeras campañas.

## 10. Resultado final obligatorio
Entregar URL de rama de implementación, SHA, PR(s), campañas y patchsets terminados, pruebas realmente ejecutadas y fallidas, decisiones pendientes, migraciones, integración con Agente y siguientes acciones. Mantener el historial íntegro y no fusionar `main`.
