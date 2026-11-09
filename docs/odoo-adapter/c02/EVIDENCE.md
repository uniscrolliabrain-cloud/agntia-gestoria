# Evidencia C02

- Odoo 19.0: `60657b50d171ddf84ab58717fdee5ac26031065b`.
- Documentación, receta, inventario de imagen y 22 fuentes fijadas con SHA-256: `infra/odoo/upstream-lock.json`.
- Resultado ejecutado de 38 comprobaciones estáticas: `static-checks.json`.
- Base de rama: main después de fusionar C01, `0626ae218983337163c569bb9dc589e98775088a`.
- CI y PR: pendientes de publicación de esta entrega; el estado real se consultará en GitHub.

La primera consulta de la documentación HTML dio timeout; se leyó su fuente oficial fijada en GitHub. La consulta Docker Hub no fue accesible; los digests se obtuvieron del inventario público de docker-library/repo-info. No se realizó pull, arranque ni petición de negocio a Odoo.
