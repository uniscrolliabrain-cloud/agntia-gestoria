# C03 — Execution Report

**Estado: EJECUTADO (local). Gate PASS para delegación verificada; integración con el runtime real NOT VERIFIED.**

- Fecha: 2026-11-16
- SHA inicial: `a523354` · SHA final: `ac8746d`
- Patchsets: PS01.1 lectura de `auth.py`, `sessions.py`, `policy.py` · PS01.2 contrato de aserción v1 · PS02.1 módulo y wiring · PS02.2 pruebas negativas · PS03.1 ejecución · PS03.2 reporte.

## Implementación
- Nuevo: `agntia_gestoria/integrations/delegation.py`. Verifica en servidor firma HMAC-SHA256 sobre el payload, `schema`, `iss`, `aud`, `iat`/`exp` con margen, rol, `sub`, `tenant`, empresas y capacidades; devuelve un `Principal` inmutable.
- `policy.py`: `authorize` y `tenant_for` aceptan principales delegados y aplican capacidades, tenant y rol sin pasar por los tokens locales. Un principal delegado nunca coincide con los actores configurados, así que no puede suplantar al owner.
- `odoo/routes.py`: dependencia `principal` (aserción delegada o token local) en todas las rutas de integración y en la auditoría de intentos fallidos.
- Nuevo: `tests/test_delegated_identity.py` — 12 pruebas.

## Propiedades garantizadas y probadas
- Rol `owner` por delegación: rechazado (401 `unsafe_principal`).
- Firma manipulada, emisor o audiencia incorrectos: 401.
- Aserción caducada: 401 `principal_revoked`.
- Capacidad fuera de la política: 403. Capacidad no delegada: 403 con mensaje explícito.
- Empresa fuera del alcance: 404.
- Rotación de clave: invalida aserciones previas.
- Sin clave configurada (<32 caracteres): 424, fail-closed.
- Aserción de más de 4 KB: rechazada antes de parsear.
- El token local sigue funcionando, sin regresión en las 37 pruebas de Odoo.

## Divergencias y límites
- `auth.py` es fichero congelado (inventario C01), así que la delegación se integra en las rutas de integración, no en todo el API. Las rutas humanas de expedientes siguen con token local. Es una decisión deliberada, no un olvido: cambiar `auth.py` exige política de fuente aprobada y ADR.
- No se ha probado contra el runtime real de Agente: no hay emisor disponible. La aserción se firma en pruebas con la misma clave.

## Rollback
Borrar `delegation.py` y revertir `ac8746d`. Sin estado persistido ni migración; las aserciones caducan solas.

## Gate
PASS local en verificación de identidad y tenancy. La compatibilidad con el runtime de Agente queda pendiente de C21/C22 y de un emisor real.
