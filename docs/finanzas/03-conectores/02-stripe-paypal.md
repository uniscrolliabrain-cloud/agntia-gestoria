# Stripe y PayPal — conectores de cobros y liquidaciones
## Objetivo
Conectar cuentas propiedad del cliente, leer pagos, cargos, comisiones, devoluciones, disputas y payouts, correlacionarlos con abonos bancarios y con facturas. Nunca tratar un charge bruto como ingreso neto ni un payout como una segunda venta.

## Stripe
Evaluar Stripe Connect (tipo de cuenta, responsabilidades, disponibilidad, requisitos KYC y comisiones) frente a OAuth/conexión directa de cuenta existente. Connect NO es requisito automático para leer datos de una cuenta; escoger modelo tras revisar el caso. Scopes mínimos; token en vault. Ingestar charges/payment_intents/balance_transactions/payouts/refunds/disputes según permisos reales. Validar firma Stripe-Signature sobre body crudo y tolerancia temporal; idempotencia por event.id + cuenta; polling de reconciliación para eventos perdidos. Nunca exponer secret keys.

## PayPal
Evaluar onboarding partner vs autorización de API empresarial; no suponer que cualquier cuenta personal permite todas las APIs. OAuth y permisos según producto/país; webhooks con verificación de firma mediante mecanismo oficial; pagos, capturas, refunds, comisiones, balances y settlements solo cuando los endpoints estén autorizados. Distinguir moneda de origen, cambio, comisión, reversión y fecha de disponibilidad.

## Modelo de conciliación
Factura 100 EUR -> cargo 100 EUR -> comisión 3 EUR -> payout 97 EUR -> abono banco 97 EUR. Son cuatro hechos distintos; no sumar 100+97 como ingresos 197. Un payout puede agrupar múltiples cargos, retenciones y refunds; matching N:M con tolerancia explícita y trazabilidad. Casos de payouts pendientes, moneda distinta, partial refunds, chargebacks y diferencias temporales.

## Operaciones prohibidas en primera fase
Refund, payout initiation, account settings, transfers, payment capture, merchant onboarding automático y actualización de datos bancarios. Futuro: propuesta y aprobación humana separadas, revisión legal y doble control.

## Tests
Firma inválida, webhook duplicado/fuera de orden, misma transacción en dos conectores, charge pendiente, payout parcial, comisión y cambio, refund posterior, disputa, paginación, rate limit, token revocado, aislamiento tenant, retry, reconciliación después de fallo.

## Evidencia y aceptación
Capturar IDs y hashes de eventos, referencias de API y saldos; fixtures sintéticos. Demostrar que una venta no se cuenta dos veces y que el reporte muestra bruto, comisiones, neto, liquidación y banco con fechas diferentes.
