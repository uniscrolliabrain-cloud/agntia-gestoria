# C23 Certificación release

Estado PLANIFICADO. Matriz de aceptación, gates seguridad, Odoo real, restauración, performance medido y decisión fundador go/no-go.

## Contrato
Entrada: tenantId/companyId/actorId verificados, correlationId, idempotencyKey, schemaVersion 1 y payload validado. Salida: status, evidenceRefs, error tipado y revision. Agente autoriza; Gestoría aplica reglas del dominio. Nunca aceptar claims del cliente como autoridad.

## Archivos y wiring
Lecturas: README.md, docs/agente-integration.md, docs/concept-master/CONCEPT-MASTER.md. Superficies candidatas a verificar: agntia_gestoria/, integrations/agente/, typescript/, tests/, infra/odoo/. Crear tests específicos y evidencias bajo esta carpeta. No modificar main ni desplegar.

## W1 discovery y contratos
PS01.1: registrar SHA, inventario real, consumidores y tests; ejecutar python -m pytest -q; resultado no ejecutado. Gate rutas verificadas. Rollback documentación.
PS01.2: schema versionado, authz, idempotencia, revocación, ADR y pruebas negativas cross-tenant; gate fail-closed. Rollback contrato previo por flag.

## W2 implementación y resiliencia
PS02.1: implementar en módulo de dominio y adaptador existente sin kernel duplicado; cablear API→policy→domain→store/outbox; test unit/integration y evidencia. Gate 0 permisos eludidos.
PS02.2: inyectar crash, timeout pre/postcommit, retry, replay y concurrencia; E2E con servicios reales si corresponde; sin Docker => BLOCKED. Gate cero duplicados. Rollback apagar escrituras y reconciliar.

## W3 certificación y reporte
PS03.1: test E2E, seguridad, performance medido, health/readiness, backup/restore, contract test y logs sanitizados. Gate PASS con evidencia; SKIP no pasa.
PS03.2: documentar SHA inicial/final, archivos, tests PASS/FAIL/SKIP, bugs/fixes, divergencias, decisiones, dependencias, riesgos, PR y handoff. No merge sin fundador.

## Execution report
Fecha PENDIENTE; rama PENDIENTE; SHAs PENDIENTE; patchsets NO EJECUTADOS; pruebas NO EJECUTADAS; bugs y decisiones PENDIENTES; rollback NO ENSAYADO.
