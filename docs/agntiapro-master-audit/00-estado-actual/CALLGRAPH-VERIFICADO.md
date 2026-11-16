# Callgraph verificado por inspección de código — 2026-11-16

Baseline main: `6b743d1e2c82885298f96a281f097d0bcbf2991a`. Evidencia directa de archivos `agntia_gestoria/auth.py`, `agntia_gestoria/integrations/odoo/routes.py`, `transport.py`, `integrations/agente/src/index.ts`, `typescript/odoo-agent-tools.ts`. Este mapa es parcial: no sustituye una ejecución de trazas.

## Identidad
HTTP request → `authenticate(request)` → `actors()` (GESTORIA_ACTORS_JSON y GESTORIA_OWNER_TOKEN) → token bearer comparado con `hmac.compare_digest` o cookie `gestoria_session` resuelta vía `sessions.resolve` → `Actor(id, role, companies)` → `company_access(actor,cid)` → `require_role` según operación. La delegación JWT de Agente NO aparece en este flujo; requerirá un adaptador seguro. Modo `GESTORIA_ALLOW_LOCAL_OWNER=true` acepta 127.0.0.1/::1/testclient solo sin actores configurados: asegurar desactivación fuera de test.

## Odoo
`register_odoo_routes(app,db)` → `APIRouter('/api/companies/{cid}/integrations/odoo')` → `Depends(authenticate)` → `Adapter(db, odoo_client_factory)` → operaciones `enqueue`, `propose_partner`, `propose_invoice`, `approve`, `commit_write`, `reconcile_write` → store/worker/transport. La ruta commit comprueba tipo de propuesta antes de llamar al adaptador. Los efectos reales de DB y approval requieren traza/test.

## Transporte
`Client.call(model,method,payload)` → allowlist READ/WRITE → write_enabled → prohibición de parámetros reservados context/allowed_company_ids/sudo/database/base_url → circuito por endpoint → `resolve_target` → `_once` con HTTP POST JSON-2, Host/SNI, allowed_company_ids del servidor, token secreto, X-Odoo-Database. `follow_redirects=False`, `trust_env=False`, timeout connect=4s total=15s, máximo de bytes, 3 intentos lectura, 1 escritura. El circuito es memoria de proceso: comprobar comportamiento multiproceso y restart. Las escrituras ambiguas exigen reconciliación por ledger, no retry ciego.

## SDK
`typescript/odoo-agent-tools.ts` → `Odoo` → `Gestoria` HTTP. Herramientas listadas no incluyen approve ni commit. `integrations/agente/src/index.ts` exporta `createGestoriaClient` con token estático de servidor, timeout 15s, y `readOnlyTools` que incluye `rrhh.closure.prepare` con `mutates:true`. Es una contradicción de clasificación verificable; comprobar consumidor y policy antes de corregir.

## Riesgos que requieren test
1. Revisión de todas las rutas que usan `company_access` y `require_role`.
2. Comprobar vínculo tenant→company→connection→DB/odoo_company en cada camino.
3. Comparar body de error del SDK (`body.detail`) con errores Odoo (`{code,message}` top-level).
4. Validar que ninguna herramienta de mutación se exponga desde `readOnlyTools`.
5. Asegurar que `companyId` en URLs TS se valida/codifica y se comprueba en backend.
6. Probar rollback, reconciliación, fallos y cambios de estado después de timeout.
