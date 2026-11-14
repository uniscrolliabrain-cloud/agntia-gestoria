# ADR 0004 · Consolidación de ramas en `main`

Fecha: 2026-11-14. Autoriza: instrucción del propietario del 2026-11-14 («lleva todo el
trabajo de ramas a main con lógica, sin desperdiciar nada, primero audita e integra y luego
cierra las ramas»). Se apoya en la autorización previa del 2026-11-11 recogida en el ADR 0003.

## Contexto

El repositorio acumulaba 17 ramas secundarias. Cinco ya estaban contenidas en `main` por las
PR #1, #2, #4, #11 y #13. Las demás se dividían en tres grupos: documentación aditiva, una
implementación de RRHH y seguridad en espacios de nombres propios, y una línea de
implementación del adaptador Odoo (C04–C06) anterior y paralela a la que consolidó la PR #4.

El inventario completo, rama por rama, con SHA y decisión, está en
[`docs/archive/branches/README.md`](../../archive/branches/README.md).

## Decisión

1. **Se integra** todo lo que añade contenido sin retirar nada: documentación de campañas,
   fábrica, implementación, RRHH y seguridad; el paquete `integrations/rrhh`; el observador
   `integrations/security`; el laboratorio de Odoo que faltaba (`lab.sh`, `smoke.py`,
   `provenance.py`, `init-role.sh`); el ADR 0002 y el harness `scripts/simulation/`.
2. **No se integra** ninguna versión de fichero anterior a la de `main` ni ningún cambio que
   altere la semántica de una pieza central. Se conserva su diff íntegro como parche en
   `docs/archive/branches/`, con justificación escrita.
3. **No se habilita** ninguna capacidad fiscal, laboral o financiera por integrar código. Los
   paquetes nuevos quedan como superficie probada, no como efecto autorizado.

## Ficheros congelados modificados en esta consolidación

El inventario C01 congela 43 ficheros. Este ADR cubre exactamente dos cambios, declarados con
sus hashes en `approved-source-changes.json`:

| Fichero | Cambio | Motivo |
|---|---|---|
| `README.md` | Enlaces a `docs/agente-integration.md`, `docs/rrhh/README.md` y `docs/seguridad/agente-ciberseguridad.md` | Las tres superficies entran en `main` y deben ser localizables desde la portada |
| `pyproject.toml` | Extras `security`, `lab` y `connectors`; `[project.urls]` | Los extras son opcionales y aditivos; el núcleo de dependencias no cambia |

`agntia_gestoria/engines.py`, `rules.py`, `territories.py`, `tax.py` y
`data/legal_sources.json` **no se tocan**: siguen protegidos y el verificador los rechazaría.

## Contrato de errores

`agntia_gestoria/integrations/errors.py` no pertenece al inventario congelado. Se amplía
`CONTRACT` con los 24 códigos que emiten `integrations/rrhh` e `integrations/security`, cada
uno con categoría y acción siguiente. Se mantiene el test que exige que todo código emitido
tenga contrato; no se relaja.

## Consecuencias

- `main` gana documentación y dos paquetes con sus pruebas; no pierde ninguna capacidad.
- Las ramas paralelas siguen siendo recuperables como parches aplicables, con sus tests.
- Los candidatos de endurecimiento detectados en el linaje C04–C06 quedan enumerados en el
  inventario y requieren un trabajo propio con regresión, no una fusión silenciosa.
- Las ramas se cierran una vez verificado que su contenido está integrado o preservado.
