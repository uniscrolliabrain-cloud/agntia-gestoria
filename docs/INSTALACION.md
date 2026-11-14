# Instalación y conexión con el repo padre

## 1 · Instalación mínima

```bash
bash scripts/install.sh          # crea .venv, instala y copia env.example a .env
.venv/bin/python -m pytest -q    # comprobación
```

Equivale a:

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp env.example .env
```

Extras disponibles, para no arrastrar dependencias que no se usan:

| Extra | Qué añade |
|---|---|
| `dev` | `pytest`, `httpx`, `playwright` |
| `security` | nada: el observador y su agente usan sólo la biblioteca estándar |
| `lab` | `psycopg[binary]` para hablar con PostgreSQL del laboratorio |
| `connectors` | `httpx` para conectores HTTP de terceros |

```bash
.venv/bin/pip install -e ".[dev,lab,security]"
```

## 2 · Configuración

`env.example` es la plantilla y `.env` tu copia local. Nunca se sube `.env`.
Las variables que importan:

- `GESTORIA_OWNER_TOKEN` y `GESTORIA_ACTORS_JSON`: quién puede hacer qué.
- `GESTORIA_RRHH_JSON`: empresas con RR. HH. encendido. Sin bandera, 404.
- `GESTORIA_RRHH_SECTOR` y `GESTORIA_RRHH_PACKS`: qué paquete de sector cargar.
- `GESTORIA_SECURITY_CHAT_WEBHOOK`: dónde avisa el agente de seguridad.

## 3 · Registro en `create_app`

Tres imports y tres líneas. No se ha publicado dentro de `app.py` porque pesa
21 KB y la herramienta de publicación rechaza ese tamaño; el diff exacto está en
[`integracion-app.md`](rrhh/integracion-app.md).

```python
from .integrations.rrhh.routes import register_rrhh_routes
from .integrations.rrhh.routes_closure import register_closure_routes
from .integrations.rrhh.routes_audit import register_audit_routes
from .integrations.security.watcher import Watcher
from .integrations.security.middleware import SecurityMiddleware
from .integrations.security.routes_security import register_security_routes
...
    app.add_middleware(SecurityMiddleware, watcher=watcher)
    register_rrhh_routes(app, db)
    register_closure_routes(app, db)
    register_audit_routes(app, db)
    register_security_routes(app, watcher)
```

`watcher` debe crearse una sola vez y compartirse: el middleware escribe en él y
el agente lee de él.

## 4 · Laboratorio ligero con Docker

```bash
docker compose -f docker-compose.lab.yml up -d                     # sólo PostgreSQL
docker compose -f docker-compose.lab.yml --profile odoo up -d      # PostgreSQL + Odoo 19
docker compose -f docker-compose.lab.yml --profile odoo down
```

PostgreSQL escucha en `5433` para no chocar con una instalación local; Odoo en
`8069`. Los volúmenes son `lab-db` y `lab-odoo`, y se borran con
`docker compose -f docker-compose.lab.yml down -v`. Nada de esto usa datos
reales ni secretos de producción.

Si el equipo prefiere no usar Docker, el servicio y las pruebas funcionan igual:
sólo el laboratorio de Odoo lo necesita.

## 5 · Conector para `uniscrolliabrain-cloud/agente`

El repo padre es pnpm + Hono con `apps/server`, `apps/web`, `packages/domain`,
`packages/workspaces` y `packages/integrations`. El conector vive en
[`integrations/agente`](../integrations/agente/README.md) y se instala copiándolo
o empaquetándolo:

```bash
pnpm --dir integrations/agente build
pnpm --dir integrations/agente pack --pack-destination ../../artifacts
pnpm add ../../artifacts/agntia-gestoria-agente-0.1.0.tgz
```

Expone sólo lectura (`capabilities`, `health`, `policy`, `closure`, `audit`,
`securityDigest`) más la preparación idempotente del cierre. `approve` y `export`
quedan fuera del catálogo agéntico: son actos humanos.

## 6 · Añadir conectores, librerías o servicios

1. Crea el módulo en `agntia_gestoria/integrations/<nombre>/`.
2. Si necesita una dependencia, añádela como extra en `pyproject.toml` y
   documenta el `pip install -e ".[<extra>]"`.
3. Registra sus rutas con una función `register_<nombre>_routes(app, db)`.
4. Si toca datos de empresa, pasa por `identifier`, `company_access` y
   `Database.put`; nunca accedas a SQLite directamente desde la ruta.
5. Si el conector es de terceros, guarda su clave en el gestor de secretos y
   pásala por variable de entorno; nada de claves en el repositorio ni en el chat.

## 7 · Qué sigue necesitando laboratorio

El lector de Odoo, la suite de integración real y las mediciones de rendimiento
requieren Odoo 19 y PostgreSQL. Con `docker compose -f docker-compose.lab.yml
--profile odoo up -d` se puede empezar; hasta entonces esos puntos siguen
marcados como BLOCKED en `pendientes.md`.
