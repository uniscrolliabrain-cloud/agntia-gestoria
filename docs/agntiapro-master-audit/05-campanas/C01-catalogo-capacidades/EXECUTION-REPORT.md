# C01 — Execution Report

**Estado: EJECUTADO (local). Gate PASS; sin merge a main.**

- Fecha: 2026-11-16
- SHA inicial: `a523354` · SHA final: `0010afd`
- Patchsets: PS01.1 lectura de `policy.py` y rutas · PS01.2 contrato v1 del manifiesto · PS02.1 módulo y CLI · PS02.2 pruebas contra openapi · PS03.1 suite · PS03.2 reporte.

## Implementación
- Nuevo: `agntia_gestoria/capabilities.py`. Deriva el manifiesto de `policy.ALL`, con `kind` (read/propose/human), `mutates`, roles, proveedor, exigencia de aprobación humana y rutas HTTP declaradas. Falla si el manifiesto y la política divergen.
- CLI: `python -m agntia_gestoria.capabilities`.
- Nuevo: `tests/test_capability_manifest.py` — 9 pruebas.
- Sin ruta HTTP nueva: añadirla habría cambiado el inventario congelado de `app.py`.

## Tests ejecutados
- `pytest tests/test_capability_manifest.py -q` → 9 passed.
- Contraste con `app.openapi()`: toda ruta declarada existe con su método (60 rutas reales).
- Reglas verificadas: ninguna lectura muta; ninguna lectura usa método distinto de GET; las capacidades humanas exigen owner/reviewer; totales cuadran con la política; el manifiesto no contiene secretos.

- Entorno: contenedor Linux, Python 3.12.3, Node v26.13.0, FastAPI 0.163.1, sin Docker ni Odoo real.
- Baseline de referencia: `python scripts/verify_baseline.py` → PASS (43 ficheros congelados, 45 rutas).
- Suites: `python -m pytest -q`, `python -m unittest discover -s tests`, `node --test integrations/agente/tests/*.test.mjs`, `tsc --noEmit`.

## Bugs y fixes
- Drift policy↔manifiesto convertido en excepción con prueba (`ghost.capability`).

## Divergencias
- El plan pedía una prueba «contra rutas reales» con endpoint propio; se resuelve contra `openapi()` sin tocar `app.py`, que es fichero congelado.

## Rollback
Revertir `0010afd`; el manifiesto es de solo lectura y no persiste nada.

## Gate
PASS local: manifiesto v1 verificable contra el servicio real. No declara cumplimiento de producto.
