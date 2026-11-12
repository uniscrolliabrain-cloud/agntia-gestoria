# Conector para el monorepo `agente`

Paquete TypeScript de solo lectura que conecta el runtime de Agente con el
middleware Gestoría. No incluye herramientas de aprobación ni de exportación:
esas dos son humanas por diseño.

## Instalación en el repo padre

El monorepo `uniscrolliabrain-cloud/agente` es pnpm + Hono. Dos caminos:

```bash
# Copiar el paquete dentro del monorepo
cp -r integrations/agente ../../agente/packages/integrations/src/gestoria

# O empaquetarlo y añadirlo como dependencia
pnpm --dir integrations/agente install
pnpm --dir integrations/agente build
pnpm --dir integrations/agente pack --pack-destination ../../artifacts
pnpm add ../../artifacts/agntia-gestoria-agente-0.1.0.tgz
```

Después, registrar el cliente en el catálogo de integraciones del servidor:

```ts
import { createGestoriaClient, readOnlyTools } from "@agntia/gestoria-agente";
import { env } from "../env.js";

const gestoria = createGestoriaClient({
  baseUrl: env.GESTORIA_URL,
  token: env.GESTORIA_TOKEN,
});

export const gestoriaTools = readOnlyTools(gestoria);
```

`companyId` se toma de la sesión autenticada del runtime, nunca de lo que
proponga el modelo. El token se guarda en el gestor de secretos del host
(Doppler en el repo padre), no en el repositorio.

## Qué expone

| Método | Endpoint del middleware | Escribe |
|---|---|---|
| `capabilities` | `GET /api/companies/{cid}/rrhh/capabilities` | no |
| `health` | `GET /api/companies/{cid}/rrhh/health` | no |
| `policy` | `GET /api/companies/{cid}/rrhh/policy` | no |
| `closure` | `GET /api/companies/{cid}/rrhh/closures/{period}` | no |
| `audit` | `GET /api/companies/{cid}/rrhh/audit` | no |
| `securityDigest` | `GET /api/security/digest` | no |

`approve` y `export` no están en el cliente agéntico: se ejecutan desde la UI
con rol humano verificado.

## Verificación

```bash
pnpm --dir integrations/agente typecheck
```

El conector no se ha compilado en este entorno porque no hay `node_modules`
instalados: el manifiesto y las firmas están revisados, no ejecutados.
