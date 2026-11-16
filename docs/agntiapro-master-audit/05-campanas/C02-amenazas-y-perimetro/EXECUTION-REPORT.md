# C02 — Execution Report

**Estado: EJECUTADO (local). Gate PASS para el perímetro del servicio HTTP.**

- Fecha: 2026-11-16
- SHA inicial: `a523354` · SHA final: `0010afd`
- Patchsets: PS01.1 inventario de controles · PS01.2 matriz de pruebas negativas · PS02.1 (sin cambios de producto: el perímetro ya existía) · PS02.2 batería adversarial · PS03.1 ejecución · PS03.2 reporte.

## Implementación
- Nuevo: `tests/test_security_boundaries.py` — 9 pruebas sobre el servicio real con `TestClient`.

## Cobertura verificada
- Empresa ajena: lectura 404 y escritura 403/404 sin filtrar identificadores.
- Orden de comprobaciones: rol antes que empresa (403), documentado como comportamiento deliberado.
- Rutas Odoo sin credencial: 401 con `code=auth`.
- Adaptador apagado: 424 `disabled` (fail-closed).
- JSON malformado: 422 tipado con `code`, `correlation_id`.
- Sentinel de credencial ausente en respuesta de error y en el export de auditoría.
- Cabeceras: `nosniff`, `DENY`, CSP con `default-src 'self'`.
- Sin configuración de actores: 403, nunca acceso anónimo.

- Entorno: contenedor Linux, Python 3.12.3, Node v26.13.0, FastAPI 0.163.1, sin Docker ni Odoo real.
- Baseline de referencia: `python scripts/verify_baseline.py` → PASS (43 ficheros congelados, 45 rutas).
- Suites: `python -m pytest -q`, `python -m unittest discover -s tests`, `node --test integrations/agente/tests/*.test.mjs`, `tsc --noEmit`.

## Bugs y fixes
- Ninguno de producto. Dos expectativas iniciales mías eran incorrectas (405 por método y 403 por rol) y se corrigieron en la prueba, no en el código: el comportamiento real es el seguro.

## Riesgos residuales
- SSRF se cubre estáticamente en `registry.py`; falta proveedor real (C07).
- No hay prueba de replay a nivel HTTP en esta campaña: vive en `tests/test_odoo_adapter.py` y se amplía en C09.

## Rollback
Revertir `0010afd`; solo pruebas.
