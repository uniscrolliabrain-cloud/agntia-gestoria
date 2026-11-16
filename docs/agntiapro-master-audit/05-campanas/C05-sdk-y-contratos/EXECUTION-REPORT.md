# C05 — Execution Report

**Estado: EJECUTADO (local). Gate PASS para el contrato de errores del consumidor.**

- Fecha: 2026-11-16
- SHA inicial: `a523354` · SHA final: `ac8746d`
- Patchsets: PS01.1 inventario de formas de error · PS01.2 contrato de parseo · PS02.1 implementación · PS02.2 pruebas por estado · PS03.1 ejecución · PS03.2 reporte.

## Bug encontrado y corregido
El cliente leía `body.detail` como si siempre fuese `{code,message}`. En las rutas de integración el error es `{code,message}` en la raíz, así que el código se perdía y quedaba `http_error`. Además `JSON.parse` se ejecutaba sin protección: una respuesta HTML de un 500 lanzaba `SyntaxError` en lugar de un error tipado.

## Implementación
- `parseFailure(status, body, statusText)`: acepta `{code,message}`, `{detail:{code,message}}`, `{detail:"texto"}`, la lista de validación de FastAPI y cuerpos no JSON, con código por estado como último recurso.
- El cuerpo no JSON nunca se propaga: no se filtra HTML ni trazas.
- `defaultStatusCode` centraliza la traducción 401/403/404/409/422/424/429/503.
- Nuevo: `integrations/agente/tests/contracts.test.mjs` — 10 pruebas con `fetchImpl` inyectado.

## Tests ejecutados
- `node --test integrations/agente/tests/*.test.mjs` → 17 passed (7 de C04 + 10 de C05).
- Casos cubiertos: 401, 403, 404, 409, 422, 503 y cuerpo vacío.
- La credencial no aparece en mensaje ni en traza; la cabecera `Authorization` se envía correctamente.

## Divergencia registrada
`typescript/index.ts` (SDK del repositorio) está en el inventario congelado y conserva `result.detail ?? result` y `response.json()` sin protección. No se modifica sin política de fuente aprobada y ADR; el endurecimiento se aplica al conector de Agente, que es el consumidor de producción. Queda como candidato P1 con su propio patchset.

## Rollback
Revertir `ac8746d`. Sin estado.
