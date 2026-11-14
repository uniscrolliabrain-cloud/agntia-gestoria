# Fase 1 · Fundación, contratos y primera capacidad

Objetivo: que exista un módulo RRHH arrancable, aislado por empresa y con contratos versionados, sin lógica de negocio todavía.

## Etapa 1.1 · Base, laboratorio y bandera por empresa

- **Nuevos:** `agntia_gestoria/integrations/rrhh/__init__.py`, `config.py`, `migrations.py`, `tests/test_rrhh_config.py`, `tests/test_rrhh_isolation.py`, `tests/fixtures/rrhh/tenants.json`, `scripts/rrhh_lab_up.py`, `scripts/rrhh_lab_down.py`.
- **Tocados:** `app.py` (una línea de registro), `auth.py` (SEC-01), `migrations.py` (índices), `.github/workflows/odoo-lab.yml` (QA-08), `requirements.txt` + `requirements.lock` (DEP-01).
- **Cableado:** `config.py` lee `GESTORIA_RRHH_JSON`, un objeto por empresa con `enabled`, `timezone`, `policy_version`, `payroll_provider`; se resuelve en el servidor y una empresa sin bandera recibe `404 capability_not_available`.
- **Tests obligatorios:** empresa sin bandera no ve nada; empresa A no puede leer objetos de B aunque conozca el identificador; `test_rrhh_local_owner_is_disabled_when_token_missing` (SEC-01); origen manipulado da 403 (SEC-04).
- **Fix bloqueante:** en `auth.py`, eliminar el propietario implícito salvo `GESTORIA_ALLOW_LOCAL_OWNER=true` y socket `testclient`, y documentarlo en `.env.example`.
- **Aceptación:** dos empresas sintéticas, suite base verde, workflow del laboratorio dispara en la rama con un run visible.

```python
# config.py, propuesto
@dataclass(frozen=True)
class RrhhConfig:
    company_id: str
    enabled: bool
    timezone: str
    policy_version: str
    payroll_provider: str | None

def config_for(company_id: str) -> RrhhConfig:
    raw = json.loads(os.getenv("GESTORIA_RRHH_JSON", "{}"))
    item = raw.get(company_id)
    if not item or not item.get("enabled"):
        raise RrhhDisabled("capability_not_available")
    return RrhhConfig(company_id, True, item["timezone"], item["policy_version"], item.get("payroll_provider"))
```

## Etapa 1.2 · Contratos de dominio y esquemas versionados

- **Nuevos:** `integrations/rrhh/contracts.py`, `docs/odoo-adapter/schemas/rrhh-v1.json`, `tests/test_rrhh_contracts.py`.
- **Tocados:** `scripts/export_contract_schemas.py` (añadir modelos RRHH), `tests/test_freebuff_backlog.py` (test de deriva ampliado).
- **Reglas de contrato:** duraciones en minutos enteros, fechas ISO con zona explícita, identificadores por ámbito, metadatos de origen separados de datos visibles, `extra="forbid"`.
- **Tests:** deriva de esquema, duración negativa rechazada, fecha sin zona rechazada, campo desconocido rechazado, `company_id` en el cuerpo rechazado aunque coincida.
- **Aceptación:** `pytest tests/test_rrhh_contracts.py` verde y el JSON regenerado idéntico al comiteado.

```python
class Punch(Model):
    id: str
    employee_ref: str
    at: AwareDatetime
    direction: Literal["in", "out"]
    source: Literal["odoo", "manual", "device"]
    source_id: str

class Absence(Model):
    id: str
    employee_ref: str
    kind: Literal["vacation", "sick", "unpaid", "other"]
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    state: Literal["approved", "pending", "refused"]
```

## Etapa 1.3 · Primera capacidad y salud del módulo

- **Nuevos:** `integrations/rrhh/routes.py`, `service.py`, `metrics.py`, `tests/test_rrhh_capabilities.py`.
- **Tocados:** `app.py` (registro), `integrations/odoo/service.py` (BUG-02: métricas fuera de `finally`).
- **Endpoints:** `GET /api/companies/{cid}/rrhh/capabilities` (versión de política, zona, proveedor, capacidades activas) y `GET /api/companies/{cid}/rrhh/health` (estado de Odoo laboral, último snapshot, antigüedad en segundos).
- **Tests:** capacidades vacías si la bandera está apagada; `viewer` puede leer salud y no capacidades de escritura; una métrica fallida no convierte una lectura correcta en error.
- **Aceptación:** `/health` responde sin credenciales de Odoo y `/capabilities` no filtra secretos.
