# PMV y vertical slices económicos
## Inventario de partida observado (lectura selectiva main, 2026-11-22)
- FastAPI Python + SQLite y SDK TS/Hono: README, agntia_gestoria/app.py, typescript/.
- Registro fiscal y CSV: agntia_gestoria/tax.py (preview, import, revisión, anulación, referencias únicas).
- Cálculo limitado modelos 303/130: agntia_gestoria/engines.py; no extrapolar a Canarias/IGIC ni presentación.
- Dashboard/reportes: README y agntia_gestoria/report_routes.py; verificar implementación y pruebas.
- Borradores locales: agntia_gestoria/app.py; no equivalen a emisión fiscal.
- Odoo: agntia_gestoria/integrations/odoo; el informe docs/odoo-adapter/final-report.md reconoce gates de proveedor no verificados.
- docs/implementation/README.md enumera 24 campañas de recuperación como PLANNED_DELTA, lo que no significa ausencia de código.

## Orden recomendado
| Slice | Entrega verificable | Dependencia externa | Gate |
|---|---|---|---|
| F01 | CSV de ingresos/gastos -> registros unverified -> evidencia -> revisión | Ninguna | duplicados, aislamiento, rollback |
| F02 | KPIs y dashboard con períodos, moneda, estado y frescura | F01 | cifras reproducibles y avisos |
| F03 | Informe PDF/HTML con procedencia y fecha | F01/F02 | paridad informe/API |
| F04 | Agenda y obligaciones como propuestas, no declaraciones | perfil empresa | reglas/fechas revisables |
| F05 | Borradores de facturas/presupuestos con aprobación | cliente y datos fiscales | no emisión automática |
| F06 | Tools read-only para LAIA/Antonio/Juan en Agente | F01-F03 | RBAC, tenant, auditoría |
| F07 | Stripe read-only y webhooks verificados | cuenta proveedor | replay/fees/refunds |
| F08 | PayPal read-only y webhooks verificados | cuenta proveedor | replay/payouts |
| F09 | Banco AIS via proveedor regulado + MCP propio | contrato proveedor/consentimiento | revocación/SCA/frescura |
| F10 | Conciliación sugerida multifuente | F07-F09 | matching no destructivo |
| F11 | Coinbase Bitcoin opt-in | modelo wallet/legal | propiedad claves y no custodia |
| F12 | Pagos/reembolsos/transferencias | validación regulatoria | aprobación humana + proveedor SCA |

## Historias conversacionales
- «LAIA, ¿cuánto ingresamos este mes y qué gastos siguen sin revisar?» -> tool autorizada, cifras con fecha y alcance, sin inventar.
- «Antonio, compara las comisiones de Stripe y PayPal y los abonos bancarios» -> origen y liquidaciones diferenciados.
- «Juan, prepara el expediente del trimestre» -> evidencias, bloqueos, revisión; no presentar declaraciones.
- «Marcos, prepara una propuesta de devolución» -> borrador y aprobación, no ejecución autónoma.
- «¿Cuánto BTC tengo?» -> saldo fuente y timestamp, no sumar BTC a EUR sin tipo de cambio, fuente y hora.

## Fuera del PMV inicial
Odoo completo, contabilidad normativa universal, declaraciones oficiales, PIS, cobros cripto automáticos, custodia de activos, trading, conversión, nóminas y conciliación bancaria irreversible.

## Estimaciones
La dificultad relativa F01-F06 es inferior a la de F09-F12; no fijar plazos sin ejecutar tests, medir integraciones y confirmar proveedores. Los gates no se declaran PASS a partir de documentos.
