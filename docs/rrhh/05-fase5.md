# Fase 5 · Módulos de RR. HH. por olas

Objetivo: ampliar cobertura sin romper el contrato del cierre. Cada módulo es una capacidad más, con su prueba de aislamiento.

## Etapa 5.1 · Ausencias y turnos

- **Nuevos:** `integrations/rrhh/modules/absences.py`, `shifts.py`, `tests/test_rrhh_absences.py`, `tests/test_rrhh_shifts.py`, `docs/rrhh/rrhh-absences.md`.
- **Tocados:** `integrations/rrhh/tools.py` (capacidades nuevas), `contracts.py` (`AbsenceRequest`, `ShiftPlan`), `schemas/rrhh-v1.json`.
- **Reglas:** saldo calculado desde snapshot, solapamiento bloqueado, revocación con historial, motivo de ausencia visible sólo al actor autorizado; turnos con plantilla, cobertura y publicación revisada; matriz de restricciones duras antes de considerar OR-Tools.
- **Tests:** solapamiento, revocación tras aprobación, cuadrante imposible, cambio después de publicar, empleado que pide la ausencia de otro (cero efectos).
- **Aceptación:** el empleado ve su historial y el responsable sólo su ámbito; ninguna ausencia se aprueba sin política versionada.

## Etapa 5.2 · Incorporación, salida y documentos

- **Nuevos:** `integrations/rrhh/modules/onboarding.py`, `documents.py`, `tests/test_rrhh_onboarding.py`, `tests/fixtures/rrhh/onboarding/*.json`.
- **Tocados:** `contracts.py` (`OnboardingTask`, `OffboardingChecklist`), `attachments.py` (reutilización del escaneo obligatorio), `vault.py` (rotación de clave, BUG-15).
- **Reglas:** alta o baja reintentada conserva un único expediente (clave estable por empleado y proceso); revocación de accesos según checklist aprobada; documento reemplazado después de solicitar firma abre conflicto.
- **Tests:** doble envío del alta, baja con tareas pendientes, documento caducado, acceso a expediente ajeno denegado.
- **Aceptación:** un alta completa y una baja completa se reproducen desde fixtures sin intervención manual.

## Etapa 5.3 · Nómina: exportación de incidencias y conciliación

- **Nuevos:** `integrations/rrhh/modules/payroll.py`, `exports/payroll_v1.py`, `tests/test_rrhh_payroll.py`, `docs/rrhh/rrhh-payroll-export.md`.
- **Tocados:** `integrations/rrhh/export.py` (manifiesto por proveedor), `contracts.py` (`PayrollIncidentExport`, `PayrollAck`).
- **Reglas:** sólo incidencias aprobadas, formato versionado con manifiesto de totales, clave estable por periodo y proveedor, acuse conciliado contra totales; resultado importado en circuito separado con cifrado y permisos; sin cálculo propio.
- **Tests:** corrección fuera de plazo, reenvío tras fallo, acuse con totales distintos (conflicto), proveedor sin configurar (capacidad no disponible), intento de leer recibos de otro empleado.
- **Aceptación:** exportación y acuse cuadran al céntimo en el fixture sintético y el reenvío no duplica nada.
