# C04 — Execution Report

**Estado: EJECUTADO (local). Gate PASS: cero herramientas mutantes en el catálogo de lectura.**

- Fecha: 2026-11-16
- SHA inicial: `a523354` · SHA final: `ac8746d`
- Patchsets: PS01.1 auditoría del conector · PS01.2 contrato de catálogos · PS02.1 separación · PS02.2 pruebas · PS03.1 ejecución · PS03.2 reporte.

## Bug encontrado y corregido
`integrations/agente/src/index.ts` declaraba `readOnlyTools` con `rrhh.closure.prepare` y `mutates: true`. Un consumidor que filtrase por pertenencia al catálogo, y no por el flag, habría ofrecido una mutación como lectura.

## Implementación
- `readOnlyTools`: cinco herramientas, todas `mutates: false`.
- `proposalTools` (nuevo): `rrhh.closure.prepare` con `mutates: true`.
- `gestoriaTools` (nuevo): unión de ambos para no romper consumidores existentes.
- `humanOnly` intacto: aprobar y exportar siguen fuera del alcance del agente.
- Nuevo: `integrations/agente/tests/catalogs.test.mjs` — 7 pruebas.

## Tests ejecutados
- `node --test integrations/agente/tests/catalogs.test.mjs` → 7 passed.
- `tsc -p tsconfig.json --noEmit` → sin errores.

## Divergencias
- El plan ubicaba la prueba en `src/tools.test.ts`; se coloca en `tests/` para que `rootDir: src` no compile tests dentro de `dist`. Se ejecuta con `node --test`, sin compilar, gracias a la sintaxis compatible con strip-types (se eliminaron propiedades de parámetro en `GestoriaError`).

## Rollback
Revertir `ac8746d`; el catálogo es código, sin estado.
