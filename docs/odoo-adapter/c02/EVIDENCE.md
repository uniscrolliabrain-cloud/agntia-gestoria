# Evidencia C02

- Odoo 19.0: `60657b50d171ddf84ab58717fdee5ac26031065b`.
- Documentación, receta, inventario de imagen y 22 fuentes fijadas con SHA-256: `infra/odoo/upstream-lock.json`.
- Resultado ejecutado de 38 comprobaciones estáticas: `static-checks.json`.
- Base de rama: main después de fusionar C01, `0626ae218983337163c569bb9dc589e98775088a`.
- PR originalmente borrador: https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/2. Fusionada por orden explicita de conservar el avance en main para el relevo, commit `1f8b7542d859ede4ea8b624fd3a4371ea603190e`; gate runtime BLOCKED.
- Revisión verificada: `09cc1cdb3994f6c978b5d0f777161d0717da8137`.
- Fuente fijada y baseline: https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676012171 — success.
- CI del servicio: https://github.com/uniscrolliabrain-cloud/agntia-gestoria/actions/runs/42676011890 — success; instalación dev, 23 tests y navegador aprobados en esa revisión.
- Esta actualización documental genera una revisión nueva que conserva sin cambios el código y los contratos verificados. Los checks del head final deben comprobarse en la PR.

La primera consulta de la documentación HTML dio timeout; se leyó su fuente oficial fijada en GitHub. La consulta Docker Hub no fue accesible; los digests se obtuvieron del inventario público de docker-library/repo-info. No se realizó pull, arranque ni petición de negocio a Odoo.
