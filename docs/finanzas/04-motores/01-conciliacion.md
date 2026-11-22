# Motor de conciliación multifuente
## Principio
Proponer enlaces entre hechos sin borrar ni modificar transacciones fuente. El usuario acepta, rechaza o deja pendiente; cada decisión genera auditoría y evidencia. No equivaler automáticamente ingreso bancario a ingreso fiscal.

## Fuentes
BankTransaction, StripeCharge, StripePayout, PayPalCapture, PayPalSettlement, InvoiceDraft, ManualRecord, CoinbaseTransaction. Crear agrupaciones por transferencias internas, payouts agrupados y comisiones.

## Pipeline
ingest -> normalize -> dedupe (source + externalId + account) -> fingerprint -> candidate generation -> deterministic scoring -> confidence tier -> proposal -> human review -> matched/split/unmatched. Guardar reglas versionadas, reason codes, evidence IDs y data freshness. Si se modifica un evento o llega refund, invalidar match y reabrir revisión.

## Reglas ejemplo
- Coincidencia fuerte: payout provider ID en descripción bancaria + moneda/importe neto + ventana de fecha.
- Coincidencia probable: importe, moneda, contraparte y ventana temporal, sin referencia inequívoca.
- Ambiguo: múltiples facturas con mismo importe; no autoaprobar.
- Diferencia: FX, comisión, retención, partial refund, chargeback o payout agregado; crear explicación, no ajustar en silencio.
- Movimientos internos entre cuentas propias no son ventas.
- BTC: conciliación on-chain separada; conversiones requieren evento FX verificable.

## Modelo de resultado
{proposalId, companyId, sourceRefs[], targetRefs[], ruleVersion, amountDifference, currency, status, confidenceBand, reasons[], blockers[], createdAt, expiresAt, approvedBy, evidenceRefs[]}. No usar confianza LLM como criterio para aprobar movimientos financieros.

## Casos dorados
1 venta única; 2 ventas payout único; payout con comisión; refund parcial; chargeback; abono bancario retrasado; moneda distinta; cuenta errónea; duplicado webhook; webhook fuera de orden; transferencia interna; pago en BTC; transacción anulada; consentimiento expirado; referencia ambigua; actualización tras aprobación.

## Gate
Reconciliación solo sugerida inicialmente. Nunca escribir en ERP/contabilidad oficial sin propuesta, revisión y permisos específicos. KPI de precisión y tasa de ambiguos medidos sobre fixtures y piloto, no inventados.
