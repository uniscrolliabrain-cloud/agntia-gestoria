# Hallazgos de segunda pasada — evidencia directa

| ID | Severidad provisional | Archivo | Evidencia | Corrección y gate |
|---|---|---|---|---|
| GES-P2-01 | Alta de diseño | `integrations/agente/src/index.ts` | `readOnlyTools` incluye `rrhh.closure.prepare` con `mutates:true` | Separar catálogo read-only de proposal/write; tests que prohíban mutates=true en catálogo de lectura |
| GES-P2-02 | Media, verificar impacto | `integrations/agente/src/index.ts` | SDK parsea `body.detail` mientras `odoo/routes.py` devuelve `code/message` top-level | Contract test 401/403/404/409/422/503; preservar códigos sin perder redacción |
| GES-P2-03 | Alta, pendiente integración | `agntia_gestoria/auth.py` | Actor se deriva de token local o sesión, no de identidad canónica de Agente | Intercambio de identidad autenticado, tenant binding server-side, revocación, anti-confused-deputy |
| GES-P2-04 | Media, pendiente live | `odoo/transport.py` | Circuit breaker `_FAILURES` en memoria de proceso | Pruebas de reinicio/múltiples workers, sin suponer circuit global |
| GES-P2-05 | Alta, gate de certificación | `odoo/routes.py`, `transport.py` | Métodos y scope declarados; no se ha probado Odoo real en esta pasada | ACL/ORM y dos DB reales, fallos pre/postcommit, reconciliación |
| GES-P2-06 | Media, revisar deployment | `auth.py` | `GESTORIA_ALLOW_LOCAL_OWNER` permite actor owner sin credenciales cuando no hay actores y request.client es loopback/testclient | Prohibir flag en despliegue no-test; test configuración negativa |
| GES-P2-07 | Media, verificar | `typescript/odoo-agent-tools.ts` | Tools proponen cambios e importan staging, sin approve/commit | Catalogar como mutaciones internas con efectos persistentes, aplicar policy/quotas y auditoría |

No se afirma explotación ni vulnerabilidad demostrada sin prueba negativa. Los SHA de blob de los archivos inspeccionados constan en GitHub. Reejecutar sobre head antes de aplicar fixes.
