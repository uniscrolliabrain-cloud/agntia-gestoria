# Campañas secuenciales — finanzas
Estado inicial: PLANNED; ninguna campaña se marca completada con esta documentación. No modificar main ni desplegar.

## Regla de ejecución por campaña
Cada agente debe registrar: baseline SHA, rama, archivos leídos, contratos existentes, diff/patchset, migraciones, dependencias, tests ejecutados y salida, riesgos, rollback, evidencias y handoff. No duplicar motores que ya funcionan. Proteger las superficies de escritura y separar PR por slice.

| Campaña | Objetivo | Superficie prevista | Gate |
|---|---|---|---|
| FIN-C00 | Baseline y auditoría código main/ramas | docs/finanzas/audits | mapa de rutas/tests real |
| FIN-C01 | Cerrar import CSV/revisión | tax.py, tests, SDK | E2E 2 empresas y duplicados |
| FIN-C02 | KPIs y dashboard | report_routes.py, frontend host | paridad de agregados |
| FIN-C03 | PDF/HTML y evidencia | report_routes.py, tests | export con provenance |
| FIN-C04 | Agenda y borradores | app.py, rules.py, models.py | estados y permisos |
| FIN-C05 | Tools Agente read-only | typescript/, adaptador host | tool RBAC + audit |
| FIN-C06 | Contratos canónicos/DB/secretos | integrations/finance, migraciones | RLS/aislamiento y restore |
| FIN-C07 | Stripe read-only | integrations/finance/stripe | webhook/replay/payout |
| FIN-C08 | PayPal read-only | integrations/finance/paypal | firma/settlement/refund |
| FIN-C09 | Banco AIS + MCP | integrations/finance/banking | consent/SCA/revocation |
| FIN-C10 | Matching y conciliación | integrations/finance/reconciliation | golden N:M |
| FIN-C11 | Coinbase Bitcoin read-only | integrations/finance/coinbase | custody decision/legal |
| FIN-C12 | UI conectores y consentimientos | apps/web en agente (tras autorización) | accesibilidad/móvil/seguridad |
| FIN-C13 | Piloto, hardening y release | CI, observabilidad, runbooks | G0-G7 con evidencia |

## Secuencia y dependencias
C00 -> C01 -> C02/C03/C04 -> C05; C06 -> C07/C08/C09 -> C10; C06 -> C11 opcional. C12 depende de contratos estabilizados. C13 tras todas las campañas seleccionadas para el alcance de release; no bloquear el PMV económico básico por Coinbase o PIS.

## Plantilla de reporte
- SHA y rama base:
- Objetivo y alcance:
- Código existente reutilizado:
- Archivos creados/modificados:
- Contratos/API y esquema:
- Tests (comandos, pass/fail, fixtures):
- Evidencia (logs redactados, hashes, capturas):
- Riesgos y dependencias:
- Rollback:
- Estado: NOT_STARTED / IN_PROGRESS / BLOCKED / VERIFIED_LOCAL / VERIFIED_SANDBOX / APPROVED_PROD
- Próximo responsable y aprobación requerida:

## No hacer
No generar credenciales ficticias como reales, no marcar gates por documentación, no insertar secrets, no llamar a pagos reales, no ejecutar merges ni despliegues automáticamente, no conectar bancos reales sin consentimiento, no escribir en ERP oficial por inferencia.
