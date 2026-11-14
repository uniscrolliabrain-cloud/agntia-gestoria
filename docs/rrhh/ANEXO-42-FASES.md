# Anexo: las 42 fases, una por una

Este anexo cierra la campaña de RR. HH. Recoge qué se implementó, con qué prueba
se sostiene y qué quedó fuera por depender de sistemas que no están en este
repositorio. La campaña de origen tenía 50 ítems numerados; se consolidaron en 42
fases de implementación porque varios ítems describían la misma pieza (por
ejemplo, «contratos» y «validación de entrada»).

Estados: **PASS** (código y prueba), **PARCIAL** (código con conector o dato
externo pendiente), **BLOQUEADO** (pertenece a otro repositorio o exige un
laboratorio que no está levantado).

| Fase | Qué hace | Módulo | Estado |
| --- | --- | --- | --- |
| 1 | Contratos versionados que rechazan campos desconocidos | `rrhh/contracts.py` | PASS |
| 2 | Ámbito resuelto desde el actor, nunca del cuerpo | `rrhh/scope.py` | PASS |
| 3 | Tiempos en minutos, zona explícita, DST absoluto | `rrhh/normalize.py` | PASS |
| 4 | Catálogo único de incidencias con norma y siguiente paso | `rrhh/issues.py` | PASS |
| 5 | Lectura paginada del origen con detección de bucle | `rrhh/source.py` | PASS |
| 6 | Registro de otra empresa detiene la lectura | `rrhh/source.py` | PASS |
| 7 | Idempotencia con conflicto por contenido distinto | `rrhh/idempotency.py` | PASS |
| 8 | Reconciliación de claves en curso | `rrhh/idempotency.py` | PASS |
| 9 | Máquina de estados con rol, motivo y evidencia | `rrhh/workflow.py` | PASS |
| 10 | Siguiente paso explícito tras cada transición | `rrhh/workflow.py` | PASS |
| 11 | Motor de cálculo determinista y versionado | `rrhh/engine.py` | PASS |
| 12 | Pausa obligatoria y jornada continuada | `rrhh/engine.py` | PASS |
| 13 | Festivos y calendario por empresa | `rrhh/packs.py` | PARCIAL |
| 14 | Snapshot inmutable con marcador de origen | `rrhh/snapshot.py` | PASS |
| 15 | Cierre con hash de resultado | `rrhh/routes_closure.py` | PASS |
| 16 | Aprobación ligada al hash del cierre | `rrhh/approval.py` | PASS |
| 17 | Exportación con manifiesto y clave estable | `rrhh/export.py` | PASS |
| 18 | Auditoría encadenada | `rrhh/audit.py` | PASS |
| 19 | Saldo de vacaciones sobre política versionada | `rrhh/absences.py` | PASS |
| 20 | Bloqueo de ausencias solapadas | `rrhh/absences.py` | PASS |
| 21 | Quien solicita no decide su ausencia | `rrhh/absences.py` | PASS |
| 22 | Revocación con motivo e historial | `rrhh/absences.py` | PASS |
| 23 | Validación de cuadrante: solape y descanso mínimo | `rrhh/shifts.py` | PASS |
| 24 | Cobertura mínima antes de publicar | `rrhh/shifts.py` | PASS |
| 25 | Publicación y nueva versión de cuadrante | `rrhh/shifts.py` | PASS |
| 26 | Alta con expediente idempotente | `rrhh/onboarding.py` | PASS |
| 27 | Baja con revocación de accesos como bloqueo | `rrhh/onboarding.py` | PARTIAL |
| 28 | Registro documental con versión y caducidad | `rrhh/documents.py` | PASS |
| 29 | Acuse de lectura idempotente | `rrhh/documents.py` | PASS |
| 30 | Cambio de versión tras pedir firma abre conflicto | `rrhh/documents.py` | PASS |
| 31 | Exportación de incidencias aprobadas a nómina | `rrhh/payroll.py` | PARTIAL |
| 32 | Acuse conciliado contra totales | `rrhh/payroll.py` | PASS |
| 33 | Reenvío con motivo y misma clave | `rrhh/payroll.py` | PASS |
| 34 | Panel con frescura del snapshot y evidencia | `rrhh/reports.py` | PASS |
| 35 | Tareas proactivas por vencimiento | `rrhh/reports.py` | PASS |
| 36 | Métricas por capacidad y percentiles | `rrhh/metrics.py` | PASS |
| 37 | Salud con causa, sin filtrar secretos | `rrhh/health.py` | PASS |
| 38 | Disyuntor con sonda y `Retry-After` acotado | `rrhh/resilience.py` | PASS |
| 39 | Matriz rol × capacidad × superficie | `rrhh/permissions.py` | PASS |
| 40 | Retención de 42 días con conservación legal | `rrhh/retention.py` | PASS |
| 41 | Copias: registro con hash y rotación | `rrhh/retention.py` | PARCIAL |
| 42 | Piloto con datos sintéticos | `source.MemorySource` | PARTIAL |

## Lo que no se pudo cerrar aquí

- **Desempeño y formación (Etapa 3)**, herramientas y SOPs del agente, y la voz
  de Anam (Etapa 4) pertenecen a `agente`. Aquí quedan como contrato y
  documentación; no se duplican.
- **Odoo real**: el lector existe contra el contrato `Source`, pero no hay
  instancia Odoo 19 + PostgreSQL levantada. El piloto usa `MemorySource`.
- **Portal y ember**: fuera de este repositorio; el middleware expone rutas y
  estados, no pantallas.
- **Suite de integración y rendimiento**: necesitan el laboratorio anterior.

## Diferencias encontradas al implementar

1. La campaña numeraba 50 ítems, pero varios eran la misma pieza vista desde dos
   sitios (contratos/validación, permisos/superficies). Consolidados en 42.
2. Los documentos de fase pedían «modelos»; se implementaron contratos propios
   con rechazo de campos desconocidos porque el origen puede cambiar sin avisar.
3. La empresa aparecía en algunos ejemplos del cuerpo de la petición. Se movió al
   actor autenticado: el cuerpo nunca decide el tenant.
4. La pausa de jornada continuada solo estaba descrita como norma; se implementó
   como regla del motor con su prueba (8 h → 465 min).
5. El descanso mínimo entre turnos no tenía número en la documentación. Se asumió
   12 h como valor por defecto configurable.
6. La nómina no se calcula aquí: se exporta lo aprobado en un formato propio
   versionado. Falta el mapeo al formato del proveedor real.
7. La retención de 42 días se tomó del nombre de la campaña; el registro horario
   obligatorio queda fuera de la purga mediante `legal_hold`.
8. Las tareas de baja no pueden cerrarse solas: si el IdP no confirma la
   revocación, el expediente queda abierto y visible.
