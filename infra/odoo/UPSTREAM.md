# Referencias reproducibles para el laboratorio

Consulta: 2026-11-09. Ver `upstream-lock.json` para URLs y SHA-256 de las 22 fuentes inspeccionadas.

- Código Community 19.0: `60657b50d171ddf84ab58717fdee5ac26031065b`.
- Documentación oficial 19.0: `67e8ded4a03d7c53be4e2c4d53471678e9e9352e`.
- Receta Docker oficial: `odoo/docker@f900094eb7492968332868d686caf22b966592ca`, directorio 19.0, paquete nightly `20261102`.
- Imagen observada: `docker.io/library/odoo:19.0-20261102`.
- Índice OCI: `sha256:5e755c725b3c43cf0be16d579904e1418300db3a2c44952f928eaddbcb0cc16d`.
- Manifest amd64: `sha256:08374de09bab5d80851c5709896aa49917e6c6a893b39025d6669db908e238b0`.

Los digests proceden de la inspección publicada en `docker-library/repo-info@afb419bc04faac713edf97eda3d9b09c63ba3cd9/repos/odoo/remote/19.0.md`, no de un pull o arranque efectuado aquí. La API web de Docker Hub no fue accesible por la herramienta de consulta; no se sustituyó por un digest inventado.

No se ha demostrado equivalencia binaria entre el paquete de la imagen de 02/11 y el SHA de código fijado el 09/11. Ambos se conservan como referencias distintas. No hay Compose ni despliegue en esta fase. PostgreSQL: mínimo 13 declarado en release.py; la versión del laboratorio y su digest deben fijarse tras verificar compatibilidad, no se afirma una prueba que no existe.

El daemon local se detectó, pero su socket denegó acceso. Un intento posterior de solicitar acceso no llegó a ejecutarse; después el entorno estuvo indisponible temporalmente. No se reinició ningún daemon ni se desplegó en otro host. Los gates de dos DB, bots, salud y restore siguen pendientes.
