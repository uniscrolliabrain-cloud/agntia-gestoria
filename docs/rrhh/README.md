# Plan RR. HH. agéntico · índice

**Estado: borrador para revisión.** Nada implementado. Estos documentos fijan contratos, ficheros, pruebas, cableado y código propuesto para que otros agentes construyan; no modifican código de la aplicación.

## Las seis fases y sus nueve etapas

| Fase | Etapa | Resultado |
|---|---|---|
| 1 · Fundación | 1.1 base, laboratorio y bandera por empresa | módulo aislado por empresa, SEC-01 cerrado |
| | 1.2 contratos y esquemas versionados | `rrhh-v1.json` sin deriva |
| | 1.3 primera capacidad y salud | `/rrhh/capabilities` y `/rrhh/health` |
| 2 · Motor de cierre | 2.1 lectura y snapshot | snapshot inmutable con hash |
| | 2.2 cálculo puro y estados | ocho fixtures dorados |
| | 2.3 aprobación, exportación e idempotencia | cierre de octubre exportado una vez |
| 3 · Odoo laboral | 3.1 addons, descubrimiento y fixtures | run reproducible con SHA |
| | 3.2 importación incremental | cursor tipado y frescura transaccional |
| | 3.3 incidencias y conciliación | ningún cierre sin actor ni evidencia |
| 4 · Superficie para agente | 4.1 catálogo de herramientas y contexto | empresa desde el host, no del cuerpo |
| | 4.2 SDK TypeScript | tipos generados, build sin deriva |
| | 4.3 eventos, outbox y trabajos | cero duplicados en reentrega |
| 5 · Módulos | 5.1 ausencias y turnos | saldo, solapamiento y publicación revisada |
| | 5.2 incorporación, salida y documentos | un único expediente por proceso |
| | 5.3 nómina: exportación y conciliación | cuadre al céntimo con el proveedor |
| 6 · Hardening | 6.1 permisos, aislamiento y secretos | matriz completa sin cruces |
| | 6.2 resiliencia, rendimiento y recuperación | medidas con tamaño de muestra |
| | 6.3 observabilidad, runbooks y piloto | checklist firmada |

## Documentos

- `00-decisiones.md`: reparto con `agente`, base de código, convenciones y hallazgos de auditoría que se cierran.
- `01-fase1.md` a `06-fase6.md`: una fase por documento, con ficheros nuevos, tocados, cableado, tests, scripts y criterios de aceptación.
- `07-trazabilidad.md`: correspondencia con la campaña del 11 de noviembre, orden de ejecución y riesgos.

## Decisión pendiente antes de empezar

`main` no contiene `agntia_gestoria/integrations/`. El plan propone que las ramas `rrhh/01-laboratorio` y `rrhh/02-middleware` nazcan de `verify/odoo-complete-adapter` (`b34b8ca`) y declaren su SHA base en cada PR.
