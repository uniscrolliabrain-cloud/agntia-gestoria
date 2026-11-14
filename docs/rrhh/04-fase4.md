# Fase 4 · Superficie para el runtime de `agente`

Objetivo: que el runtime consuma capacidades cerradas sin poder ampliar permisos ni inventar contexto.

## Etapa 4.1 · Catálogo de herramientas y contexto de host

- **Nuevos:** `integrations/rrhh/tools.py`, `context.py`, `docs/rrhh/rrhh-tools.md`, `tests/test_rrhh_tools.py`.
- **Tocados:** `integrations/rrhh/routes.py` (`GET .../rrhh/tools`, `POST .../rrhh/tools/{name}`), `integrations/policy.py` (verificación del contexto).
- **Reglas:** entrada limitada a periodo, identificador autorizado y filtros admitidos; identidad, empresa y correlación de encargo vienen del host autenticado, nunca del cuerpo; resultado estructurado con `next_allowed` y `evidence_ref`.
- **Tests:** cuerpo con `company_id` ajeno rechazado; actor `viewer` no ejecuta; correlación ausente da `correlation_required`; instrucciones incrustadas en un campo de texto se devuelven como dato, no se ejecutan.
- **Aceptación:** el catálogo cabe en un JSON versionado y una herramienta nueva sin contrato rompe la suite de deriva.

```python
TOOL_NAMES = ("rrhh.snapshot.prepare", "rrhh.closure.read", "rrhh.issue.list", "rrhh.export.prepare")

def invoke(name: str, payload: dict, ctx: HostContext) -> ToolResult:
    if name not in TOOL_NAMES:
        raise Reject("unknown_tool", next_action="list_tools")
    service = SERVICES[name]
    return service(payload, ctx)   # ctx.company_id manda; payload.company_id se descarta
```

## Etapa 4.2 · SDK TypeScript

- **Nuevos:** `typescript/rrhh.ts`, `typescript/types/rrhh.d.ts`, `typescript/tests/rrhh.test.mjs`.
- **Tocados:** `typescript/index.ts` (export), `typescript/package.json` (exports), `dist/` regenerado, `scripts/export_contract_schemas.py` si el cliente se genera.
- **Reglas:** el cliente sólo acepta la capacidad y el periodo; los tipos se generan del esquema `rrhh-v1.json`; ningún token se guarda en el navegador.
- **Tests:** tipos contra el JSON, error tipado con `category` y `next_action`, reintento que conserva la clave de idempotencia, `build.mjs` sin deriva.
- **Aceptación:** `node --test typescript/tests/rrhh.test.mjs` verde y `git status --short` limpio después del build.

## Etapa 4.3 · Eventos, outbox y trabajos técnicos

- **Nuevos:** `integrations/rrhh/events.py`, `jobs.py`, `tests/test_rrhh_events.py`, `tests/test_rrhh_jobs.py`.
- **Tocados:** `integrations/migrations.py` (índice único `integration_inbox(company_id, event_id, consumer_id)`), `integrations/odoo/jobs.py` (lease y reintentos).
- **Reglas:** evento con `schemaVersion`, acuse idempotente por consumidor, cursor con caducidad; trabajo con lease, barrido de arranque y aviso de huérfanos.
- **Tests:** reentrega, evento manipulado, cursor expirado, proceso muerto con trabajo `running`, dos trabajos con la misma clave.
- **Aceptación:** cero efectos duplicados en la matriz de reentrega, y ningún trabajo queda `running` sin alerta.
