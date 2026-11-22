# Seguridad, gobernanza y análisis regulatorio
Este documento es una lista de verificación técnica, no asesoramiento jurídico ni certificación.

## Matriz de acciones
| Capacidad | PMV | Quién autoriza |
|---|---|---|
| Ver saldos/movimientos | Sí, tras consentimiento y RBAC | Titular/proveedor + policy runtime |
| Ver cobros y liquidaciones | Sí, scopes de lectura | Titular/proveedor + policy |
| Conciliación sugerida | Sí | Runtime; revisión humana para consolidar |
| Emitir factura fiscal | No | Futuro sistema validado |
| Reembolsar/cobrar | No | Revisión legal, humano y proveedor |
| Iniciar transferencia PIS | No | Licencia/modelo contractual y SCA aplicable |
| Crear wallet de cliente | Solo onboarding verificado | Titular + proveedor |
| Custodiar claves/cripto | No | Fuera de alcance |
| Comprar/vender BTC/USDC | No | Fuera de alcance |

## Riesgos a revisar
PSD2/AIS/PIS y rol de AgntiaPro, proveedor AISP/PISP y contratos; RGPD (responsables/encargados, DPA, retención, transferencias, DPIA cuando proceda); PCI DSS si se procesan datos de tarjeta (preferir checkout alojado/tokenizado); DORA si aplicable según entidad/rol; MiCA/CASP, AML y Travel Rule según servicio cripto; normativa fiscal y facturación España/Canarias. No prometer «sin licencia» sin dictamen contextual.

## Seguridad
OAuth state/PKCE donde aplique, validación redirect, vault/KMS, secretos rotables, tokens de corta duración, webhook HMAC/verificación oficial, protección SSRF, límites de payload, egress allowlist, RBAC/ABAC tenant/empresa, separación lectura/escritura, MFA en operaciones sensibles, rate limit, circuit breaker, auditoría inmutable, redacción de PII, backups cifrados, restore probado, revocación y eliminación. Nunca exponer MCP remoto sin gateway de política. Validar que tool output es dato no confiable (prompt injection).

## Threat model mínimo
Cross-tenant leak, confusión de cuentas, token theft, consent replay, webhook spoofing, idempotency collisions, double booking, currency errors, malicious transaction memo, compromised agent, forged approvals, seed phrase leak, chain reorg, stale balances, unauthorized refund/payment, provider outage.

## Release gates
G0 contrato proveedor, producto y cobertura confirmados; G1 threat model/privacidad/roles; G2 tests sintéticos aislados; G3 sandbox E2E con dos empresas; G4 revisión humana y consentimiento/revocación; G5 observabilidad/backup/restore; G6 piloto supervisado; G7 aprobación explícita de producción. G0-G7 permanecen OPEN hasta evidencia.
