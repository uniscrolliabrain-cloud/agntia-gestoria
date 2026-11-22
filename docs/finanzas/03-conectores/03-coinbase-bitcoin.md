# Coinbase / Bitcoin — wallet opcional
## Intención
El fundador quiere facilitar a cada empresa cliente una wallet Bitcoin con tecnología o servicios Coinbase, ligada a su panel financiero. No asumir que AgntiaPro puede crear cuentas Coinbase Exchange en nombre de terceros ni que Coinbase CDP, Coinbase Wallet y Coinbase Commerce sean el mismo producto. La disponibilidad y términos actuales se deben verificar directamente con el proveedor antes de elegir.

## Decisión pendiente: custodia
A. **Self-custody:** cliente controla claves y recuperación; AgntiaPro facilita onboarding o enlace de dirección pública, solo lectura on-chain o mediante proveedor. Preferida para prototipo sin control de fondos, siempre evaluando UX y seguridad.
B. **Custodial por proveedor:** cuenta/wallet creada y custodiada por proveedor bajo términos y KYC del cliente, si el producto lo permite; AgntiaPro solo orquesta y lee permisos autorizados.
C. **Custodia por AgntiaPro:** excluida. No generar/almacenar seed phrases ni claves privadas en servidor propio.

## Bitcoin versus stablecoins
Bitcoin BTC y USDC son activos diferentes, con redes, custodia, riesgo, precio y tratamiento fiscal diferentes. No prometer liquidación USDC en Coinbase como característica inherente a una wallet BTC. Si se desea USDC, especificar red, producto, elegibilidad, off-ramp y riesgos por separado.

## Flujo seguro inicial
1. Cliente decide activar módulo opcional y recibe información sobre riesgos y privacidad.
2. Selecciona wallet externa compatible o producto Coinbase validado y completa personalmente KYC si aplica.
3. Vincula wallet por dirección pública y prueba de control cuando sea necesaria; nunca pide seed.
4. Backend guarda walletId, red, dirección pública, titular declarado, estado de verificación, consentimiento, proveedor y fechas.
5. Consultas read-only de saldos/transacciones con confirmaciones y altura de bloque; proteger privacidad de direcciones.
6. Reportes muestran BTC/sats, EUR de referencia con fuente y timestamp, comisiones de red y estado pendiente/confirmado. No se considera efectivo bancario.

## Controles
No enviar BTC, firmar transacciones, intercambiar, comprar/vender, hacer staking, recuperar seeds ni hacer retiros. Separar fondos de cliente y empresa. Validar network/address, chain reorgs, doble contabilización, confirmaciones, reuso de dirección, polvo/spam, límites y screening proporcional. Protección de datos y evaluación AML/sanciones si corresponde.

## Gate jurídico
Analizar MiCA/CASP, AML, Travel Rule, publicidad y fiscalidad aplicable en UE/España; determinar si AgntiaPro presta servicios de criptoactivos o solo software informativo. La ausencia de custodia NO garantiza por sí sola ausencia de obligaciones. Validar condiciones Coinbase y jurisdicción. No publicitar servicio como wallet custodiada por AgntiaPro antes de la evaluación.

## Tests
Dirección inválida/red errónea, reorg, 0 confirmaciones, depósitos repetidos, transferencias internas, cambio BTC/EUR, proveedor offline, datos cruzados y filtración de direcciones.
