# Ensayo previo con el runtime de Agente

Se probó Gestoría con el código del adaptador de la [PR #4](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/4), el cambio de cierre de la [PR #12](https://github.com/uniscrolliabrain-cloud/agntia-gestoria/pull/12) y Agente en el commit `b37b67d4e18987402d255d377343a3454d723e5e`. El ensayo levantó FastAPI en loopback sobre SQLite temporal y usó el JavaScript compilado del SDK, la versión Hono de Agente y las clases reales `AgentRuntimeManager`, `CapabilityRunner` y `Executor`. El registro de herramientas, la política y el almacén de claims del escenario de escritura fueron dobles controlados.

## Resultados

| Caso | Observado |
| --- | --- |
| Lectura desde el runtime | Una capacidad de lectura resolvió un expediente real de la empresa de la sesión sintética. |
| Separación de empresas | Hono recibió 404 al consultar otra empresa. El runner denegó el otro tenant antes de llamar al executor. El executor rechazó un ID de empresa inyectado en la entrada. |
| Cierre y revisión | El agente recibió 403 para revisar y cerrar. El cierre ya no figura en sus herramientas y el propietario completó el expediente revisado. El caso base permite reproducir el cierre anterior. |
| Reentrega de un registro | El mismo `external_id` devolvió 409 y se conservó una sola fila. |
| Escritura con ACK perdido | Un efecto sintético aplicó un cambio y lanzó un error. `CapabilityRunner` guardó el claim como `failed` y volvió a ejecutar el efecto al repetir la misma operación. Se observaron dos ejecuciones del efecto simulado. |

El último caso bloquea el uso directo de mutaciones Odoo como herramientas de Agente. Los comandos aprobados deben mantener su clave estable y reconciliar el resultado incierto en Gestoría. Una futura capacidad de escritura en el runtime debe demostrar que un timeout posterior al commit se conserva como `outcome_unknown` y que repetir el paso no vuelve a ejecutar el efecto.

El ensayo de este documento tiene Odoo desactivado. Quedan por probar la integración con Odoo real desde un runtime desechable, la resolución de identidad del host y el consumo de cambios. La simulación no instala el SDK en Agente.

## Reproducir

En el checkout de Agente, instalar únicamente sus dependencias con `pnpm install --frozen-lockfile --ignore-scripts`. En Gestoría, instalar las dependencias de desarrollo y construir el SDK con `node typescript/scripts/build.mjs`. Ejecutar:

```text
python scripts/simulation/run.py --gestoria <checkout-gestoria> --agente <checkout-agente>
```

Con `--baseline` el ensayo espera que el SDK y la API conserven el cierre por agente y reproduce ese resultado. El directorio temporal y sus credenciales se crean durante la ejecución.
