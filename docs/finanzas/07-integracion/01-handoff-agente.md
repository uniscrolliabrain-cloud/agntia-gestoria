# Handoff — integración Gestoría ↔ AgntiaPro
## Contexto
Repositorio origen: uniscrolliabrain-cloud/agntia-gestoria (Python FastAPI/SQLite, TS SDK/Hono). Host previsto: uniscrolliabrain-cloud/agente (Node/TS, runtime SOP/policy/event bus). Esta rama es solo documentación; no se ha inspeccionado ni modificado el host durante esta entrega.

## Puntos de inspección antes de escribir código
Origen: README.md, agntia_gestoria/app.py, tax.py, engines.py, models.py, storage.py, report_routes.py, integrations/odoo/, typescript/index.ts, typescript/odoo-agent-tools.ts, tests/. Host: buscar rutas actuales de tool registry, policies, tenant context, secrets, events, SOP executor y workspace financiero; no asumir paths históricos.

## Integración sugerida
- Adaptador server-to-server autenticado con principal por empresa, no owner global.
- Herramientas: finance_list_accounts, finance_get_balances, finance_list_transactions, finance_get_kpis, finance_get_unreviewed, finance_generate_report, finance_list_reconciliation_proposals, finance_connection_status.
- Herramientas write separadas: finance_propose_match; finance_approve_match solo para principal humano con rol y revisión, nunca agent token.
- LAIA presenta resultados y deriva análisis; Antonio calcula con hechos; Juan revisa fiscalidad y documentación; Marcos ejecuta SOPs permitidos.
- Event outbox -> bus append-only con id, schemaVersion, tenantId, companyId, correlationId/causationId, source, occurredAt, payload con referencias; ACK solo tras persistencia idempotente.
- Respuesta UI: dato + período + moneda + origen + observedAt + estado de revisión + advertencias. La IA no calcula impuestos o tipos de cambio de memoria.

## Contrato de ejemplo (propuesta, no endpoint actual)
finance_get_kpis({companyId, from, to, currency}) -> {income, expense, simpleNet, pendingReviewCount, sources[], observedAt, incomplete, warnings[]}. No llamar simpleNet beneficio contable.

## Pruebas obligatorias
Dos tenants/tres roles, empresa ajena 403, token revocado, payload malicioso, proveedor lento, timeout, doble webhook, doble contabilización, documento cambiado, consentimiento expirado, no leaked secrets, app móvil, outbox replay, backup/restore.

## Orden de entrega
Auditar host actual -> estabilizar contratos -> implementar adaptador read-only -> pruebas contractuales -> E2E sintético -> habilitar UI con flags OFF por defecto -> autorización del fundador. No hacer merge/deploy sin aprobación.
