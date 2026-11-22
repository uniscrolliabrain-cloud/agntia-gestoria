# Banca española — Open Banking PSD2 y MCP
## Intención
El cliente enlaza sus cuentas con consentimiento explícito. AgntiaPro consulta saldos y movimientos autorizados y los presenta por empresa, con frescura y procedencia. No solicitar credenciales de banca online al cliente ni hacer screen scraping no autorizado.

## Aclaración crucial
**MCP no es una licencia bancaria, ni una API PSD2, ni un consentimiento.** Es una interfaz de herramientas que puede envolver un servicio AIS/PIS regulado. Verificar por país y banco las capacidades de Tink, TrueLayer, Enable Banking, Plaid u otros; no afirmar cobertura de BBVA, Santander, CaixaBank, Qonto o entidades específicas sin prueba contractual y sandbox. La situación regulatoria depende del papel de cada parte, subcontratación, acceso a datos, iniciación de pagos y jurisdicción. No asumir que el cliente aporta consentimiento y por ello AgntiaPro queda automáticamente exenta de toda obligación.

## Arquitectura propuesta
Agente -> policy engine (tenant/actor/scope) -> Finance Tool Registry -> adapter MCP controlado -> backend AIS del proveedor autorizado -> banco; callback OAuth/SCA en canal proveedor/usuario; vault para tokens. MCP no se expone públicamente sin autenticación y autorización fuerte.

## Flujo AIS
1. Owner selecciona proveedor, banco y cuenta; acepta aviso de privacidad y permisos granulares.
2. Backend crea sesión de conexión con nonce/state, redirect permitido y binding tenant/empresa.
3. Cliente realiza SCA en flujo oficial; proveedor devuelve token de conexión al backend.
4. Se verifica identidad de cuenta, consent scope, expiry, permissions, bankId, accountId y moneda.
5. Se ingieren saldos/movimientos por cursor y ventana temporal; se registran observación, fuente, timestamps y errores.
6. Se ofrece revocación, reconexión, eliminación de acceso y gestión de retención.
7. Si el consentimiento caduca o falla, UI indica dato antiguo y bloquea sincronización.

## PIS (FUERA DE ALCANCE)
La iniciación de pagos requiere evaluación separada de permisos, responsabilidad, fraude, SCA y contrato; no se permite al agente ordenar pagos ni simular firma del cliente. El proceso de autorización varía por banco, proveedor y exenciones SCA: no afirmar que cada pago siempre requiere el mismo desafío.

## Seguridad de MCP
Tool schemas cerrados (get_accounts, get_balances, list_transactions, connection_status); sin herramienta HTTP arbitraria, sin URLs suministradas por LLM, sin OAuth tokens en tool output. mTLS/HTTPS, allowlist, scopes, rate limiting, timeout, audit, replay protection, prompt-injection boundary y control de egress.

## Criterios de aceptación
Dos empresas sintéticas no ven cuentas cruzadas; consentimiento revocado detiene lectura; caducidad no produce saldos presentados como actuales; duplicados/reordenamiento no duplican movimientos; proveedor caído degrada sin datos inventados; webhooks/callbacks validan firma/state; export y borrado sujetos a política.

## Preguntas abiertas
Proveedor contratado y titular del contrato; condición regulatoria de cada actor; disponibilidad real AIS/PIS España; coste y límites; periodicidad de refresh; alcance de cuentas empresariales; política de conservación; DPA/subencargados; compatibilidad Canarias/UE.
