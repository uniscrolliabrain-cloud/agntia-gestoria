# Fase 2 · Motor determinista del cierre

Objetivo: «prepara el cierre de octubre» reproducible, con snapshot inmutable, cálculo puro, estados verificados y exportación con aprobación.

## Etapa 2.1 · Lectura acotada y snapshot inmutable

- **Nuevos:** `integrations/rrhh/reader.py`, `snapshot.py`, `tests/test_rrhh_reader.py`, `tests/test_rrhh_snapshot.py`, `tests/fixtures/rrhh/october-2026/` (empleados, fichajes, ausencias, calendario).
- **Tocados:** `integrations/rrhh/routes.py` (`POST .../rrhh/snapshots`), `migrations.py` (verificar índice por `company_id`, `kind` y `unique_key`).
- **Reglas:** el periodo, la zona y el calendario se resuelven en servidor; paginación keyset por `(write_date, id)`; cualquier objeto fuera de ámbito aborta antes de normalizar; el snapshot guarda hash, versión de política, fecha de corte y los registros fuente completos necesarios para explicar una incidencia.
- **Fix incluido (BUG-03):** la frescura se comprueba dentro de `BEGIN IMMEDIATE` y se revalida al escribir; si la fuente cambió, `409 source_changed_since_snapshot`.
- **Tests:** 1.200 fichajes sin duplicar ni perder; dos objetos con el mismo `write_date`; cambio remoto entre lectura y escritura; snapshot repetido con el mismo origen devuelve el existente (misma clave).
- **Aceptación:** dos snapshots idénticos del mismo corte producen el mismo `sha256`.

```python
def build_snapshot(connection, config, period) -> dict:
    with Database.transaction(connection):
        sources = read_bounded(connection, config, period)   # IO dentro de la transacción
        verify_freshness(sources, period)                    # relee write_date máximo
        body = {"company_id": config.company_id, "period": period.isoformat(),
                "policy_version": config.policy_version, "timezone": config.timezone,
                "cutoff_at": now(), "sources": sources}
        body["content_hash"] = digest(body)
        Database.put(connection, config.company_id, "rrhh_snapshot", body,
                     unique_key=f"snapshot:{period.isoformat()}:{body['content_hash']}")
    return body
```

## Etapa 2.2 · Cálculo puro y máquina de estados

- **Nuevos:** `integrations/rrhh/engine.py` (sin IO), `state.py`, `tests/test_rrhh_engine.py`, `tests/test_rrhh_state.py`, `tests/fixtures/rrhh/golden/*.json`.
- **Reglas:** intervalos que cruzan medianoche, dos cambios de horario, pausas, jornada parcial, festivo por centro; duplicados, fichaje incompleto y ausencia pendiente generan incidencia en vez de horas; estados `prepared → blocked | pending_review → approved → exported` y `reconciliation_required`; cada transición persiste actor, motivo y evidencia.
- **Tests dorados:** ocho fixtures con horas y motivos esperados, incluidos centro equivocado y edición posterior a la aprobación (que reabre revisión).
- **Aceptación:** el mismo snapshot y la misma versión de política dan el mismo resultado byte a byte; cambiar solo la política cambia el resultado y el hash.

```python
def close_period(snapshot: dict, policy: Policy) -> Closure:
    # función pura: sin conexión, sin reloj, sin entorno
    ...
    return Closure(hours_by_employee=..., issues=..., totals=..., content_hash=digest(payload))
```

## Etapa 2.3 · Aprobación, exportación e idempotencia

- **Nuevos:** `integrations/rrhh/approval.py`, `export.py`, `commands.py`, `tests/test_rrhh_approval.py`, `tests/test_rrhh_export.py`, `tests/test_rrhh_idempotency.py`.
- **Tocados:** `integrations/errors.py` (códigos `closure_not_approved`, `source_changed_since_approval`, `export_conflict`).
- **Reglas:** la aprobación liga hash del cierre, empresa, revisión de política y actor con rol `owner` o `reviewer`; un cambio de origen reabre revisión; la exportación lleva clave estable y manifiesto de totales e incidencias; repetición con la misma clave devuelve el mismo resultado y con contenido distinto da `409`.
- **Tests:** aprobación caducada, aprobación de otro actor, dos exportaciones concurrentes con la misma clave (un solo objeto), caída antes y después del efecto.
- **Aceptación:** el cierre de octubre sintético se exporta una sola vez y el manifiesto cuadra con las horas del fixture dorado.
