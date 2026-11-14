# Plan RR. HH. agéntico · 6 fases × 3 etapas · documento de revisión

Estado: **borrador para revisión**. Este documento no implementa nada: fija contratos, ficheros, pruebas, cableado y el código propuesto que otros agentes escribirán. Nada de lo aquí descrito habilita escrituras de Agente.

## Decisiones que hay que aprobar antes de empezar

1. **Reparto.** El agente, Anam, la conversación, los SOPs, el entrenamiento y el portal viven en `agente`. Este plan es solo `agntia-gestoria`: middleware determinista, permisos, reglas, Odoo, evidencia, aprobación e idempotencia.
2. **Base de código.** `main` (`d3e81ad`) **no contiene** `agntia_gestoria/integrations/`; el adaptador de Odoo, el contrato de errores y la retención viven en `verify/odoo-complete-adapter` (`b34b8ca`). Propuesta: las ramas de implementación `rrhh/01-laboratorio` y `rrhh/02-middleware` nacen de esa rama, no de `main`, y cada PR declara su SHA base. Alternativa si se exige `main`: una primera etapa de aterrizaje del adaptador, que este plan contaría como fase 0 no prevista.
3. **Rama del documento.** `recursos-humanos`, creada desde `main` (`d3e81ad`), solo contiene documentación.
4. **Datos.** Todo sintético. Los addons `hr`, `hr_attendance` y `hr_holidays` de Odoo Community 19 son el primer recorrido; `hr_recruitment` y `hr_expense` quedan fuera de las seis fases.
5. **Nada de cálculo de nómina propio.** La fase 5 exporta incidencias y concilia acuses; el cálculo pertenece al proveedor.

## Convenciones que el código debe respetar

- Rutas por registro: `register_rrhh_routes(app, db)` llamado desde `create_app`, después de `register_odoo_routes`. Nunca se edita `app.py` para lógica de dominio.
- Persistencia en la tabla `objects` con `kind` nuevos (`rrhh_employee`, `rrhh_punch`, `rrhh_absence`, `rrhh_issue`, `rrhh_closure`, `rrhh_export`), sin migración destructiva; índices nuevos en `migrations.py` con `IF NOT EXISTS`.
- Errores por el contrato existente (`errors.py`): códigos nuevos con categoría y `next_action`, nunca `str(exc)` al cliente.
- Toda operación lleva `company_id` desde el contexto autenticado, nunca desde el cuerpo.
- Cada mutación escribe auditoría encadenada (`db.audit`) con hash de contenido.
- Pruebas en `tests/` con `pytest`, datos en `tests/fixtures/rrhh/`, y sufijo `_synthetic` en cualquier fichero de laboratorio.

## Lo que este plan arregla de la auditoría del 11 de noviembre

| Hallazgo | Dónde se cierra |
|---|---|
| SEC-01 propietario implícito en loopback | Fase 1 · etapa 1 (bloqueante: sin esto no se expone dato laboral) |
| SEC-04 origen por cabecera `Host` | Fase 1 · etapa 1 |
| SEC-13 y BUG-01 upsert sin empresa ni clave | Fase 1 · etapa 2 (helpers de escritura con `company_id` y `unique_key`) |
| BUG-02 métricas en `finally` | Fase 1 · etapa 3 (métricas fuera del camino de error) |
| BUG-03 frescura fuera de transacción | Fase 2 · etapa 1 y fase 3 · etapa 2 |
| BUG-07 y BUG-13 retención y copias | Fase 6 · etapa 2 |
| QA-08 workflow contradictorio | Fase 1 · etapa 1 |
| OPS-01 y OPS-02 salud y logging | Fase 6 · etapa 3 |
| DEP-01 sin lockfile | Fase 1 · etapa 1 |
