# Jornada, fichaje, turnos, vacaciones y bajas

Objetivo: registro horario defendible ante la Inspección, cuadrantes que respetan descansos y nocturnidad, vacaciones con saldo correcto y bajas que no rompen el cierre.

## Etapa 11.1 · Fichaje y registro diario

- **Nuevos:** `agntia_gestoria/integrations/rrhh/time/clock.py`, `corrections.py`, `tests/test_rrhh_clock.py`, `tests/fixtures/rrhh/punches/*.json`.
- **Tocados:** `routes.py` (`POST .../rrhh/punches`, `POST .../rrhh/punches/{id}/correct`, `GET .../rrhh/timesheet`), `contracts.py`.
- **Reglas:** hora de inicio y fin por persona y día (art. 34.9 ET); **conservación 4 años**; corrección con autor, motivo y original conservado (nunca borrado); resumen mensual para tiempo parcial con la nómina (art. 12.4.c); el sistema es digital por diseño, pero no afirma que la ley lo exija, porque el real decreto sigue sin publicarse.
- **Tests:** corrección con original conservado, fichaje duplicado, descanso de 12 horas incumplido (incidencia, no bloqueo silencioso), exportación a Inspección sin datos de otra empresa, retención a 4 años.

```python
def correct_punch(connection, company_id, punch_id, fix, actor) -> dict:
    original = Database.get(connection, company_id, punch_id, "rrhh_punch")
    corrected = {**original, **fix, "corrected_by": actor.id, "corrected_at": now(),
                 "supersedes": original["id"], "id": uid()}
    Database.put(connection, company_id, "rrhh_punch", corrected,
                 unique_key=f"punch:{corrected['employee_ref']}:{corrected['at']}")
    Database.audit(connection, company_id, actor, "rrhh.punch.corrected", corrected["id"], corrected)
    return corrected
```

## Etapa 11.2 · Turnos, rotaciones y nocturnidad

- **Nuevos:** `time/shifts.py`, `coverage.py`, `tests/test_rrhh_shifts.py`.
- **Tocados:** `packs/*.json` (parámetros de turnos), `routes.py` (`POST .../rrhh/shifts/plan`, `POST .../rrhh/shifts/publish`).
- **Reglas:** noche de 22:00 a 06:00; máximo 8 horas diarias de promedio en 15 días para nocturnos; sin horas extra para nocturnos; **ninguna persona más de 2 semanas seguidas en noche** salvo adscripción voluntaria; descanso semanal de día y medio; cuadrante publicado con revisión y con historial de cambios.
- **Tests:** rotación que incumple las dos semanas, cobertura insuficiente, cambio tras publicar (nueva versión, no sobrescritura), persona de baja que deja hueco, festivo por centro.
- **Aceptación:** un cuadrante imposible se rechaza explicando la restricción y la norma, no con un error genérico.

## Etapa 11.3 · Vacaciones, permisos y bajas

- **Nuevos:** `time/leave.py`, `absences.py`, `tests/test_rrhh_leave.py`, `tests/test_rrhh_sick_leave.py`.
- **Tocados:** `routes.py` (`POST .../rrhh/leave/request`, `POST .../rrhh/leave/{id}/approve`, `POST .../rrhh/sick-leave`), `engine.py` (las ausencias entran en el cálculo).
- **Reglas:** **30 días naturales** mínimos o los superiores del convenio; calendario conocido con **2 meses** de antelación; vacaciones no sustituibles por dinero salvo extinción; IT que coincide con vacaciones se disfruta después, con **18 meses** desde el final del año para contingencias comunes y sin límite en embarazo, parto o lactancia; permisos del art. 37.3 con sus días exactos; nacimiento y cuidado de 19 semanas (32 en monoparentalidad).
- **Tests:** solapamiento, saldo insuficiente, vacaciones durante IT, permiso de 5 días por hospitalización de familiar, baja que cruza el cierre del mes, reincorporación tras 545 días.
- **Aceptación:** el saldo de vacaciones cuadra con convenio y antigüedad, y ninguna baja desaparece del cierre por estar abierta.

## Datos que el motor debe poder explicar

Cada incidencia y cada línea de nómina debe poder responder: qué hecho la genera, qué regla del pack se aplicó, qué norma la respalda y qué dato original la sustenta. Sin eso, el cierre no es defendible ante una revisión.
