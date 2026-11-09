# Integración futura con AgntiaPro y agentes

No se ha modificado `uniscrolliabrain-cloud/agente`. Aplicar wiring allí requiere aprobación del propietario. Este documento es el patchset conceptual revisable; no presupone que el runtime exista.

## SDK servidor Hono/pnpm

El root Git es un paquete Python. Para instalar en un repo Hono/pnpm, empaquetar el subdirectorio: `pnpm --dir RUTA/agntia-gestoria/typescript pack --pack-destination RUTA/artifacts` y después `pnpm add RUTA/artifacts/agntia-gestoria-0.1.0.tgz` desde el repo consumidor. No apuntar pnpm al root Git como si tuviera package.json. No se ha publicado en npm/PyPI durante esta entrega.

```typescript
import { Gestoria } from '@agntia/gestoria';
import { Odoo } from '@agntia/gestoria/odoo';
import { odooAgentTools } from '@agntia/gestoria/odoo-agent-tools';
const api = new Gestoria(process.env.GESTORIA_URL!, process.env.GESTORIA_TOKEN!);
const erp = new Odoo(api, companyIdVerifiedByServer);
const tools = odooAgentTools(erp);
```

URL y token solo en servidor. companyId se deriva de la sesión verificada, no de la propuesta del LLM. Usar una credencial de servicio por scope; no un owner universal para las herramientas. El proxy Hono existente tiene allowlist exacta de rutas/métodos Odoo. El paquete `/odoo` ofrece métodos humanos de approve/commit; no entregarlos a las herramientas agénticas.

`ODOO_IDENTITY_MODE=integrated` exige `ODOO_ACTOR_SCOPES_JSON`, por actor autenticado, con tenant, companies y capabilities. Las capacidades del gateway deben ser aprovisionadas administrativamente y coincidir con las credenciales existentes; un header tenant o un nombre Laia/Marco no acredita identidad.

## Herramientas y roles

Las herramientas cerradas permiten salud, preview/import, status, conflictos, propuesta de contacto/factura y briefing. Ninguna permite ejecutar ORM libre, aprobar o clasificar. Juan prepara y explica; Antonio analiza solo métricas de origen acreditado; Marco propone/ejecuta SOP autorizado; Laia consume hechos y supervisa. Las capacidades se asignan a principales, nunca a una personalidad.

Eventos outbox con schemaVersion, tenantId, companyId, correlationId, causationId, occurredAt y payload de referencias sin secretos. Consultar `/events`, procesar idempotentemente por id y ACK solo después de persistir en el runtime. Nombres implementados incluyen sync.completed, conflict.detected, review.required, connection.degraded e invoice_draft.created bajo prefijo gestoria.odoo.

## Rota como contrato

Diaria 08–09 hora de empresa: validar salud, lanzar preview/sync, listar registros/documentos pendientes y preparar briefing con fuentes. Cierre diario: solo acciones realmente persistidas. Semanal: revisión de excepciones y documentos por Juan, anomalías de caja de fuentes verificadas por Antonio. Mensual: preparación de cierre y reportes con ámbito legal explícito. La agenda pertenece al Organizational Runtime de AgntiaPro; este repo no añade otro scheduler ni aparenta actividad.

Antes del wiring: verificar gateway, policy/approval service, backpressure del event bus, ownership por campo, retención, presupuesto de retries y revocación. La versión standalone ya exige aprobación humana local; no hay aprobación fingida como sustituto de un servicio externo.
