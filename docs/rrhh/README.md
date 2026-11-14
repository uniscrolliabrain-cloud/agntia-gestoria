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

## Ampliación: dominio laboral completo

- `08-marco-legal.md`: normas con artículo y fecha (ET, LGSS, RGPD, Reglamento de IA, cotización 2026) y lo que obligan a codificar.
- `09-metaestructura.md`: ontología, política y reglas por sector como dato; compilación con suelos legales y hash.
- `10-contratacion.md`: modalidades, validaciones, SEPE, altas y coste con tipos de 2026.
- `11-jornada-vacaciones.md`: fichaje, correcciones, turnos, nocturnidad, vacaciones, permisos y bajas.
- `12-extincion-finiquitos.md`: indemnizaciones con dos tramos, finiquito, colectivo, ERTE y FOGASA.
- `13-talento-formacion.md`: vacantes, CV, supervisión humana, FUNDAE, onboarding y PRL.

## Decisiones pendientes antes de empezar

1. `main` no contiene `agntia_gestoria/integrations/`: se propone que las ramas `rrhh/01-laboratorio` y `rrhh/02-middleware` nazcan de `verify/odoo-complete-adapter` (`b34b8ca`) y declaren su SHA base.
2. Revisión de un laboralista de cada regla del pack antes de activarla en una empresa real.
3. Confirmar los tipos de AT/EP por CNAE con la tarifa vigente antes de dar cifras de coste.
