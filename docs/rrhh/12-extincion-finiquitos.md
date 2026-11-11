# Extinción, despidos y finiquitos

Objetivo: calcular indemnizaciones y liquidaciones con la norma vigente, generar la documentación y no permitir un efecto sin aprobación humana.

## Etapa 12.1 · Motor de indemnizaciones

- **Nuevos:** `agntia_gestoria/integrations/rrhh/termination/indemnity.py`, `tranches.py`, `tests/test_rrhh_indemnity.py`, `tests/fixtures/rrhh/termination/*.json`.
- **Tocados:** `routes.py` (`POST .../rrhh/terminations/estimate`), `packs/compiler.py`.
- **Reglas:** disciplinario procedente 0 €; improcedente **33 días/año** con tope de 24 mensualidades; objetivo y colectivo **20 días/año** con tope de 12 y **15 días** de preaviso (30 en colectivo); fin de temporal **12 días/año** sin tope; contratos anteriores al 12/02/2012 con **45 días** hasta esa fecha y 33 después, tope de **720 días** salvo tramo previo superior y límite absoluto de 42 mensualidades.
- **Tests:** antigüedad de 2 años antes de 2012 y 14 después (45 × 2 + 33 × 14 = 552 días); tope de 720 alcanzado; tope de 24 mensualidades; temporal con 12 días; cálculo con salario diario que incluye prorrata de pagas.

```python
def indemnity_days(start: date, end: date, kind: Literal["objective", "unfair", "temporary"]) -> Decimal:
    if kind == "temporary":
        return Decimal(years(start, end)) * 12
    if kind == "objective":
        return min(Decimal(years(start, end)) * 20, Decimal(365))
    # despido improcedente, con dos tramos para contratos anteriores al 12/02/2012
    cut = date(2012, 2, 11)
    first = Decimal(years(start, min(end, cut))) * 45 if start <= cut else Decimal(0)
    second = Decimal(years(max(start, cut), end)) * 33
    return min(first + second, max(Decimal(720), first))
```

## Etapa 12.2 · Finiquito y liquidación

- **Nuevos:** `termination/settlement.py`, `tests/test_rrhh_settlement.py`.
- **Tocados:** `routes.py` (`POST .../rrhh/terminations/{id}/settlement`), `contracts/engine.py` (plantilla de carta).
- **Conceptos:** salario pendiente, pagas extra devengadas (o prorrata si ya están prorrateadas), **vacaciones devengadas y no disfrutadas**, horas extra pendientes, preaviso no trabajado e indemnización. La indemnización no cotiza hasta su límite legal y está exenta de IRPF hasta ese límite; las vacaciones pagadas retrasan el inicio de la prestación por desempleo.
- **Reglas:** propuesta de liquidación junto al preaviso (art. 49.2 ET); sin plazo legal único de pago, pero con interés de mora del **10 % anual** si se retrasa el salario; el trabajador puede firmar "no conforme"; nada se descuenta sin acuerdo o resolución.
- **Tests:** finiquito con pagas prorrateadas (no se duplican), vacaciones parciales, preaviso trabajado y no trabajado, horas extra con recargo de cotización, firma "no conforme" que no bloquea el pago.

## Etapa 12.3 · Despido colectivo, ERTE y FOGASA

- **Nuevos:** `termination/collective.py`, `fogasa.py`, `tests/test_rrhh_collective.py`, `docs/rrhh/rrhh-erte.md`.
- **Reglas:** umbrales del art. 51.1 ET en 90 días (10 en menos de 100, 10 % de 100 a 300, 30 en más de 300); periodo de consultas de 30 días (15 en menos de 50); **ERTE y RED no extinguen** y no generan indemnización; FOGASA hasta **11.373,60 €** en salarios y **34.594,70 €** en indemnizaciones en 2026.
- **Tests:** umbral superado que obliga a procedimiento colectivo, ERTE que no genera finiquito, tope de FOGASA aplicado, despido objetivo sin indemnización puesta a disposición (se marca improcedente).
- **Aceptación:** ningún cálculo se ejecuta sin `policy_hash`, actor autorizado y registro de auditoría; el sistema **nunca** envía la carta ni ejecuta el despido.
