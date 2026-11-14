# Metaestructura dinámica: ontología, política y reglas por sector

Objetivo: que una empresa nueva se configure **sin tocar código**: se carga su sector, su convenio y sus datos, y el sistema compila una política con suelos legales, reglas evaluables y plantillas. El código es genérico; el sector es dato.

## 1. Piezas

```text
SectorPack (dato, versionado, con fuente y SHA)
  ├── ontologia:  conceptos, roles, categorías y relaciones del sector
  ├── politica:   parámetros (jornada anual, vacaciones, prueba, preavisos, pluses)
  ├── reglas:     condiciones → consecuencias, cada una con base_legal
  ├── plantillas: contrato, finiquito, carta, checklist de incorporación
  └── tablas:     salarios por grupo, festivos por centro, tipos de cotización del ejercicio

EmpresaConfig (por tenant)
  ├── sector_id + convenio (código REGCON, ámbito, vigencia, sha256)
  ├── centros, calendario, zona horaria, política de fichaje
  └── overrides permitidos (solo si mejoran el suelo legal)
```

## 2. Esquema propuesto

- **Nuevos:** `docs/rrhh/esquemas/sector-pack.schema.json`, `agntia_gestoria/integrations/rrhh/packs/loader.py`, `validator.py`, `compiler.py`, `tests/test_rrhh_packs.py`, `tests/fixtures/rrhh/packs/{hosteleria,comercio,tecnologia}.json`.

```json
{
  "sector_id": "hosteleria",
  "version": "2026.1",
  "convenio": {"codigo": "REGCON-…", "ambito": "provincial", "vigencia": "2026-2028", "sha256": "…"},
  "ontologia": {
    "roles": ["camarero", "cocinero", "jefe_sala"],
    "categorias": [{"id": "G3", "nombre": "Técnico", "salario_base_anual": 20794.47}],
    "relaciones": [{"tipo": "sustitucion", "aplica_a": ["camarero", "cocinero"]}]
  },
  "politica": {"jornada_anual_h": 1715, "vacaciones_dias_laborables": 23, "prueba_meses": 2,
               "preaviso_dias": 15, "nocturnidad": true, "turnos": true},
  "reglas": [
    {"id": "vacaciones.minimo", "cuando": {"tipo": "empleado"}, "entonces": {"vacaciones_min": 30, "unidad": "dias_naturales"}, "base_legal": "art. 38.1 ET"},
    {"id": "prueba.limite", "cuando": {"grupo": "tecnico_titulado"}, "entonces": {"prueba_max_meses": 6}, "base_legal": "art. 14.1 ET"}
  ]
}
```

## 3. Compilación y validación

- `loader.py` lee el pack, verifica `sha256` y esquema, y **rechaza** cualquier pack sin `base_legal` en sus reglas.
- `validator.py` compara el pack con los **suelos legales** del ejercicio (`legal_floor.py`): si una regla deja al trabajador peor que el ET, el pack no compila.
- `compiler.py` produce una `CompiledPolicy` inmutable con hash; el hash se guarda en el snapshot y en la aprobación, de modo que un cambio de política se detecta igual que un cambio de datos.
- Precedencia explícita: **suelo legal → convenio → acuerdo de empresa → contrato individual**, y cada nivel solo puede mejorar el anterior en materias indisponibles.

```python
def compile_policy(pack: SectorPack, company: CompanyConfig, floor: LegalFloor) -> CompiledPolicy:
    problems = validate_pack(pack, floor)          # devuelve lista, no excepciones sueltas
    if problems:
        raise PackRejected(problems)               # 422 con detalle por regla
    merged = merge(pack.politica, company.overrides, precedence=("legal", "convenio", "empresa"))
    return CompiledPolicy(sector=pack.sector_id, version=pack.version,
                          rules=pack.reglas, params=merged, sha256=digest(merged))
```

## 4. Reglas evaluables

- Las reglas se evalúan con hechos (`facts`) tipados: tipo de contrato, grupo, antigüedad, jornada, centro, fecha.
- Cada evaluación devuelve `{rule_id, outcome, base_legal, explain}` para que la respuesta del API pueda citar la norma y la persona pueda revisarla.
- Una regla sin `base_legal`, o con una referencia que no exista en el catálogo de normas, **rompe la compilación**.
- Sin código ejecutable dentro del pack: nada de expresiones arbitrarias. Predicados cerrados (`eq`, `in`, `gte`, `lt`, `between`) para que un pack no pueda convertirse en un vector de ejecución.

## 5. API y almacenamiento

- `GET /api/companies/{cid}/rrhh/policy` devuelve política compilada, hash y normas citadas.
- `POST /api/companies/{cid}/rrhh/policy/preview` compila con datos nuevos sin guardar (para el alta de empresa).
- `GET /api/rrhh/sectors` y `GET /api/rrhh/sectors/{id}/versions` leen del catálogo publicado.
- Persistencia en `objects` como `rrhh_sector_pack` y `rrhh_policy`, con `unique_key = sector:version:sha256`.

## 6. Pruebas de la metaestructura

- `test_pack_without_legal_basis_is_rejected`: una regla sin norma no compila.
- `test_pack_cannot_lower_the_legal_floor`: vacaciones de 22 días o prueba de 9 meses se rechazan.
- `test_two_sectors_compile_independently`: hostelería y tecnología producen políticas distintas con el mismo motor.
- `test_policy_hash_changes_only_with_the_policy`: cambiar un dato de empresa no altera el hash de la política.
- `test_pack_version_is_pinned_in_snapshot`: el snapshot recuerda con qué versión se calculó.
- `test_unknown_predicate_is_rejected`: un pack con un predicado no soportado no carga.

## 7. Cómo se añade un sector nuevo (sin código)

1. Se copia un pack existente y se ajustan ontología, política, reglas y plantillas.
2. Se rellena `convenio` con código, ámbito, vigencia y SHA del texto publicado.
3. Se ejecuta `scripts/rrhh_pack_validate.py packs/nuevo.json` y se revisan los avisos.
4. Se publica con `POST /api/rrhh/sectors` (rol `owner`) y queda versionado.
5. Al dar de alta la empresa, se elige sector y convenio; el sistema compila y muestra las normas aplicables antes de guardar.

**Criterio de aceptación:** un sector nuevo entra en producción sin desplegar código, y cualquier política resultante es explicable regla a regla con su norma.
