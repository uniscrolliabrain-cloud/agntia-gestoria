# Arquitectura y taxonomías
## Capas
1. **Fuentes:** CSV/manual, facturas locales, Odoo opcional, bancos AIS, Stripe, PayPal, Coinbase.
2. **Adapters:** SDK HTTP oficial cuando proceda; OAuth/consent; validación de firma de webhooks; mapeo tipado.
3. **Ingestión:** raw evidence cifrada/restringida, cursor, checkpoint, idempotencyKey, sourceVersion, jobs, DLQ.
4. **Modelo canónico:** FinancialAccount, Connection, Consent, BalanceSnapshot, Transaction, Charge, Payout, Fee, Refund, Dispute, InvoiceDraft, TransferProposal, Wallet, CryptoTransfer, FXQuote, ReconciliationMatch, Evidence, Approval.
5. **Motor:** normalización, deduplicación, matching determinista, agregación, discrepancias, frescura, auditoría.
6. **Tools:** contratos cerrados y de mínimo privilegio para runtime Agente; MCP solo como transporte/descubrimiento de herramientas, nunca como frontera de autorización.
7. **UX:** dashboard, fuentes conectadas, transacciones, pendientes, conciliación, informes, consentimientos, historial.

## Identidad obligatoria
tenantId, companyId, principalId, connectionId, accountId, sourceSystem, externalId, eventId, correlationId, causationId, schemaVersion, observedAt, effectiveAt, currency, amountMinor, status, evidenceRef. Usar unidades menores enteras por divisa o Decimal estricto; BTC en satoshis, no float. Distintos balances: available, pending, ledger, provider-specific. Evitar netear saldo con deuda o pagos pendientes.

## Estados de conexión
not_connected -> onboarding -> consent_pending -> active -> degraded/reauth_required -> revoked/expired. Un estado revoked corta llamadas inmediatamente y programa borrado/retención conforme a política aplicable; conservar únicamente evidencias exigibles y permitidas.

## Estados de transacción
observed -> normalized -> pending_review -> reviewed; invalidated/superseded con versiones. No modificar la fuente original; correcciones como nueva versión enlazada. Separar posted, pending, failed, reversed, refunded, disputed y settled según origen.

## Eventos de dominio propuestos
finance.connection.created, finance.consent.expired, finance.sync.completed, finance.sync.failed, finance.transaction.observed, finance.payout.observed, finance.reconciliation.proposed, finance.reconciliation.approved, finance.reconciliation.conflict, finance.wallet.linked, finance.review.required. Payload solo IDs y metadatos seguros; schemaVersion y tenant scope obligatorios.

## Endpoints sugeridos (NO implementados por este documento)
GET /finance/connections, POST /finance/connections/{provider}/onboarding, POST /finance/connections/{id}/revoke, GET /finance/accounts, GET /finance/transactions, GET /finance/balances, GET /finance/payouts, POST /finance/reconciliation/preview, POST /finance/reconciliation/{id}/approve, GET /finance/reports, GET /finance/audit.
Separar /proposals y /approvals de /execute; no exponer /execute en PMV.

## Taxonomía de permisos
finance.connections.manage, finance.accounts.read, finance.transactions.read, finance.balances.read, finance.reports.read, finance.reconciliation.propose, finance.reconciliation.approve, finance.wallet.read, finance.payments.propose, finance.payments.execute (OFF), finance.refunds.execute (OFF), finance.crypto.transfer (OFF). La política evalúa usuario real y autorización explícita; el agente no se autoconcede scopes.

## Taxonomía de errores
auth_required, consent_expired, permission_denied, tenant_scope_violation, provider_unavailable, rate_limited, stale_data, ambiguous_match, currency_mismatch, duplicate_event, signature_invalid, reconciliation_required, unsupported_capability. Respuestas sanitizadas sin payload bancario completo.

## Diseño de almacenamiento
Preferir adaptador a infraestructura central Agente con aislamiento fuerte y cifrado. No reutilizar SQLite local sin evaluar concurrencia, backup/restore, RLS, rotación y recuperación multiempresa. Las claves privadas nunca en DB de aplicación ni prompts.
