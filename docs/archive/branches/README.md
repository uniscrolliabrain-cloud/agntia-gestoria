# Consolidación de ramas en `main` · 2026-11-14

Registro de la auditoría de las 17 ramas secundarias de `agntia-gestoria` y de lo que se
integró en `main`, lo que se preservó como parche y lo que se descartó por regresión. El
objetivo es que ninguna rama se cierre sin que su contenido esté identificado y recuperable.

Criterio aplicado:

1. Se integra lo que **añade** contenido o capacidad sin quitar nada de `main`.
2. Se integra código nuevo en espacios de nombres propios (`integrations/rrhh`,
   `integrations/security`) aunque su rama de origen fuera antigua.
3. **No** se integra una rama cuando su versión de un fichero es anterior a la de `main` o
   cambia la semántica de una pieza de la que depende el resto del sistema. En ese caso se
   conserva su diff íntegro como parche y se documenta la decisión.
4. Nada se marca como verificado si no se ha ejecutado.

## 1 · Ramas ya contenidas en `main`

Sin trabajo pendiente: su contenido llegó por PR #1, #2, #4, #11 y #13.

| Rama | SHA | Integración previa |
|---|---|---|
| `feat/odoo-c01-baseline` | `8178680` | PR #1 (fusionada) |
| `feat/odoo-c02-upstream-audit` | `df989be` | PR #2 (fusionada) |
| `feat/odoo-complete-adapter` | `81043b0` | PR #4 (fusionada) |
| `verify/odoo-complete-adapter` | `b34b8ca` | base técnica de PR #11 |
| `freebuff/gestoria-autonomo` | `5b45fc1` | PR #13 (fusionada) |

## 2 · Ramas integradas en esta consolidación

| Rama | SHA | Qué se ha integrado |
|---|---|---|
| `docs/factory-recovery-v1-20261114` | `1c1bb0d` | 62 documentos nuevos: `docs/campaigns/` (24 campañas + manifiesto), `docs/factory/` (10), `docs/implementation/` (25), `docs/prep/` |
| `recursos-humanos` | `876bc2d` | 15 documentos `docs/rrhh/` (decisiones, fases 1–6, trazabilidad, marco legal, metaestructura, contratación, jornada, extinción, talento) |
| `rrhh/01-laboratorio` | `60e4267` | Código: `integrations/rrhh/` (31 módulos), `integrations/security/` (7 módulos), 19 tests, `docker-compose.lab.yml`, conector `integrations/agente/`, `Makefile`, `scripts/install.sh`, `docs/INSTALACION.md`, `docs/seguridad/`, `docs/rrhh/ANEXO-42-FASES.md`, `docs/rrhh/integracion-app.md`, fixtures de convenio, extras de `pyproject.toml` |
| `feat/odoo-c03-lab` | `01ec1c5` | Laboratorio que faltaba en `main`: `infra/odoo/lab.sh`, `smoke.py`, `provenance.py`, `init-role.sh`, `README.md`, `.gitattributes`, `.gitignore` |
| `fix/odoo-adapter-human-case-closure` | `bf05473` | `docs/odoo-adapter/adr/0002-human-case-closure.md`, `docs/odoo-adapter/agente-simulation.md`, `scripts/simulation/` (`run.py`, `probe.mjs`, `runtime-probe.mts`) |
| `codex/odoo-c02-runtime-verification` | `0e181ac` | `docs/odoo-adapter/c02/WINDOWS-VERIFICATION.md` (evidencia Windows, Docker ausente, criterio de salida) |
| `docs/campana-integracion-agente` | `cf9f685` | `docs/agente-integration.md` y un enlace desde `README.md`. Su `README.md` era anterior al adaptador; no se revierte el actual |
| `docs/handoff-freebuff` | `43c7fc7` | Enlaces relativos y comando `fetch` correcto en `docs/handoff-freebuff-2026-11-10.md` |

## 3 · Ramas preservadas como parche (no fusionadas)

Sus implementaciones son una **línea de diseño paralela**, anterior a la consolidación de la
PR #4. Sustituirlas obligaría a reescribir `integrations/odoo/service.py`, `routes.py`,
`commands.py` y el resto del adaptador, cuyas tablas y contratos son distintos. Fusionarlas
tal cual retrocedería `main` (diferencias de −7 900 líneas en los diff de dos puntos).

Cada parche es un `git diff` completo desde el punto de bifurcación: se puede aplicar,
revisar o comparar sin haber perdido una sola línea.

| Parche | Rama | Base | Contenido |
|---|---|---|---|
| `feat-odoo-c04-contracts.patch` | `feat/odoo-c04-contracts` (`fd5abc6`) | `1fd25d9` | Contratos de lectura/staging con `Contract`, `AwareDatetime`, versión estricta |
| `feat-odoo-c05-storage.patch` | `feat/odoo-c05-storage` (`3b35d4d`) | `1fd25d9` | Migraciones aditivas con backup, concurrencia e idempotencia |
| `feat-odoo-c06-registry.patch` | `feat/odoo-c06-registry` (`f3c40dd`) | `1fd25d9` | Registro de conexiones por tenant, `ServerCatalog`, rotación y desactivación |
| `fix-human-case-closure.patch` | `fix/human-case-closure` (`78ca93b`) | `1fd25d9` | Cierre de expedientes reservado a roles humanos |
| `rrhh-propuesta-auth-storage.patch` | `rrhh/01-laboratorio` | `main` | Propuesta de `auth.py`/`storage.py` y sus 2 tests |

### 3.1 · `fix/human-case-closure`: intención ya cubierta

La rama reserva el cierre de expedientes a `owner`/`reviewer`. `main` **ya lo aplica**:

```python
# agntia_gestoria/app.py · close_case
require_role(actor,*REVIEW)   # REVIEW = ('owner','reviewer')
```

Además, el `app.py` de la rama es anterior a la PR #4 y eliminaría las sesiones de navegador,
los endpoints `/health/live` y `/health/ready` y el registro de rutas Odoo. Se conserva como
parche por trazabilidad; su comportamiento ya está en `main`.

### 3.2 · `rrhh/01-laboratorio`: por qué no se integran `auth.py` y `storage.py`

El código RRHH (`integrations/rrhh`, `integrations/security`) **sí** se ha integrado: no
colisiona con nada y solo depende de `auth.authenticate` y `storage.identifier`, que se
mantienen. Lo que no se integra es su versión de dos ficheros núcleo:

- `auth.py` de la rama elimina la resolución de sesiones (`sessions.resolve`) y el hash de
  sesión. `app.py`, `/api/login`, `/api/logout` y `sessions.py` de `main` dependen de ello:
  aplicarlo rompería el inicio de sesión del navegador.
- `storage.put` de la rama difiere en dos puntos: reemplaza `unique_key` siempre (también
  cuando llega nulo, mientras `main` conserva el anterior vía `COALESCE`) y convierte el
  rechazo entre empresas en `PermissionError` en lugar de `FileNotFoundError`. El ADR 0003 ya
  documenta que `main` actualiza la clave cuando se proporciona una nueva, así que la
  diferencia real es el caso nulo y el tipo de excepción. Cambia el contrato del que dependen
  `tax.py`, `app.py`, el adaptador y sus tests: requiere una decisión explícita y su
  regresión propia, no una fusión silenciosa.

Ambos diff están en `rrhh-propuesta-auth-storage.patch`, con sus tests
(`test_auth_local_owner.py`, `test_storage_hardening.py`) para poder retomarlo con una
regresión propia.

## 4 · Candidatos de endurecimiento pendientes de portar

Del linaje c04–c06 hay controles que `main` **no** tiene y que merecen un trabajo aparte, con
sus propias pruebas (no se han portado a ciegas):

- `approved_origin()`: rechaza hosts con etiquetas puramente numéricas o hexadecimales
  (`0x7f.1`), fija ASCII imprimible, prohíbe `\ % ? #`, canonicaliza `netloc` y exige que el
  host esté en una allowlist nombrada. `main` valida esquema, credenciales en URL y CIDR,
  pero no la forma del nombre.
- `ServerCatalog`: detecta alias duplicados de endpoint y de base de datos.
- `secret()`: exige `[!-~]{16,512}`, más estricto que la longitud mínima actual.
- Registro con tablas propias por tenant (`odoo_connections`, `odoo_company_scopes`) frente
  a `provider_connections` de `main`.

## 5 · Estado de verificación

- Los cambios de esta consolidación son aditivos o de espacios de nombres nuevos.
- La suite completa se ejecuta tras la integración; el resultado se registra en el PR de
  consolidación, no en este documento.
- Ninguna capacidad fiscal, laboral o financiera se habilita por integrar código: los
  paquetes RRHH y seguridad quedan como superficie documentada y probada, no como efecto
  autorizado.
