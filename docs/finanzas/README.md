# Finanzas — visión, arquitectura y plan de PMV
Estado: DOCUMENTACIÓN / DISEÑO, no funcionalidades desplegadas. Rama: finanzas. Fecha: 2026-11-22.

## Intención del fundador
Construir una experiencia de gestión económica empresarial conversacional para autónomos y pymes: LAIA presenta y coordina; Antonio analiza finanzas; Juan revisa gestión y fiscalidad; Marcos ejecuta SOPs autorizados. Los agentes no son la fuente de verdad: el runtime determinista consulta registros, proveedores y evidencias. El cliente conecta **sus propias cuentas** bancarias, PayPal y Stripe; AgntiaPro facilita además el alta guiada de una wallet Bitcoin mediante un producto elegible de Coinbase, evitando por defecto la custodia por AgntiaPro. Unificar movimientos, saldos y cobros, detectar diferencias y preparar conciliaciones, con trazabilidad y revisión humana.

## Índice
- [01 — Alcance y slices](01-producto/01-pmv-y-slices.md)
- [02 — Taxonomía y modelo](02-arquitectura/01-taxonomia-y-modelo.md)
- [03 — Conectores](03-conectores/01-banca-psd2-mcp.md), [Stripe/PayPal](03-conectores/02-stripe-paypal.md), [Coinbase/Bitcoin](03-conectores/03-coinbase-bitcoin.md)
- [04 — Conciliación y ledger](04-motores/01-conciliacion.md)
- [05 — Seguridad, regulación y riesgos](05-gobernanza/01-seguridad-regulacion.md)
- [06 — Campañas y aceptación](06-campanas/01-plan-secuencial.md)
- [07 — Handoff de integración](07-integracion/01-handoff-agente.md)

## Invariantes
1. LLM propone; sistema dispone. Nunca derivar saldo o movimiento de texto libre del modelo.
2. Deny-by-default; por empresa, actor, cuenta, permiso, proveedor y propósito.
3. Lectura primero. AIS, balances, movimientos y cobros no implican autorización para PIS, transferencias, refunds ni retiros.
4. No credenciales bancarias en prompts, frontend, logs, eventos o repositorio. Tokens y claves en vault; acceso mínimo.
5. Idempotencia, audit append-only, correlationId, outbox, reintentos acotados y reconciliación tras timeout.
6. Separar origen proveedor, asiento contable, operación bancaria, liquidación, comisión, devolución y conversión de moneda.
7. Una wallet o dirección Bitcoin no es una cuenta bancaria ni una cuenta de custodia necesariamente. Elegir explícitamente modelo custodial/no custodial.
8. Sin datos bancarios ni clientes reales hasta verificación jurídica, contratos, seguridad, DPA y pruebas de aislamiento.
9. Proveedores, productos, disponibilidad por país, permisos, precios, licencias y capacidades MCP son **hipótesis a verificar** antes de escoger implementación.
10. Mantener separadas las capacidades existentes en main de este diseño futuro; no confundir README/contrato con pruebas E2E.

## Definición de éxito
Un cliente autoriza lectura de fuentes disponibles, observa dashboard económico con procedencia y frescura, identifica cobros Stripe/PayPal y movimientos bancarios, ve conciliaciones sugeridas y aprueba manualmente excepciones. Wallet Bitcoin opcional, nunca necesaria para el PMV base. Sin pagos automáticos ni custodia de fondos.
