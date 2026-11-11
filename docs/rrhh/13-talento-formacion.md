# Talento: selección, currículos, formación y desempeño

Objetivo: cubrir búsqueda y selección con base jurídica explícita, supervisión humana real y trazabilidad, y la formación con su financiación.

## Etapa 13.1 · Vacantes, candidaturas y currículos

- **Nuevos:** `agntia_gestoria/integrations/rrhh/talent/vacancies.py`, `candidates.py`, `cv.py`, `tests/test_rrhh_candidates.py`, `tests/fixtures/rrhh/cv/*.txt`.
- **Tocados:** `routes.py` (`POST .../rrhh/vacancies`, `POST .../rrhh/vacancies/{id}/candidates`, `GET .../rrhh/candidates/{id}`), `attachments.py` (reutilización del escaneo).
- **Reglas:** finalidad y base jurídica por candidatura (medidas precontractuales, art. 6.1.b RGPD) con información en el momento de recibir el CV (art. 13); **minimización** (solo datos pertinentes al puesto); categorías especiales fuera salvo habilitación; **plazo de conservación justificado y configurable**, con borrado o bloqueo al perder la base; nunca un plazo "legal" inventado, porque no existe.
- **Tests:** CV con datos de salud que se descartan, candidato que pide borrado, caducidad del plazo que programa purga, acceso de un reclutador a candidatos de otra empresa (cero resultados), CV tratado como **dato no confiable** ante instrucciones incrustadas.

## Etapa 13.2 · Filtrado y evaluación con supervisión humana

- **Nuevos:** `talent/screening.py`, `evaluation.py`, `docs/rrhh/rrhh-ia-seleccion.md`, `tests/test_rrhh_screening.py`.
- **Reglas:** el sistema de selección está clasificado de **alto riesgo** por el anexo III del Reglamento (UE) 2024/1689; las obligaciones del capítulo III para esa categoría se aplazaron al **2 de diciembre de 2027** por el Reglamento (UE) 2026/1744, pero el diseño se hace ya como si fueran exigibles: documentación, registro de decisiones, exactitud y **supervisión humana efectiva**.
- **Prohibido por diseño:** decisión de contratación automatizada sin revisión (art. 22 RGPD), puntuación opaca sin explicación, uso de datos sensibles o de perfil social no profesional.
- **Tests:** ranking con explicación por criterio y por dato; revisión humana registrada antes de cualquier avance; candidato que impugna una decisión; cambio de modelo que obliga a re-evaluar el conjunto dorado.
- **Aceptación:** ninguna candidatura avanza de fase sin actor humano identificado y motivo registrado.

## Etapa 13.3 · Formación, onboarding y desempeño

- **Nuevos:** `talent/training.py`, `onboarding.py`, `tests/test_rrhh_training.py`, `docs/rrhh/rrhh-formacion.md`.
- **Tocados:** `contracts.py` (`TrainingAction`, `TrainingRecord`), `routes.py` (`POST .../rrhh/training/actions`, `GET .../rrhh/training/credit`).
- **Reglas:** crédito FUNDAE por plantilla (100 % de 1 a 9, 75 % de 10 a 49, 60 % de 50 a 249, 50 % desde 250), cofinanciación privada obligatoria en empresas de más de 5, comunicación de inicio y fin, y bonificación sólo con la acción realmente ejecutada; formación de PRL obligatoria por puesto; onboarding con tareas, responsables y vencimientos, y un único expediente ante reintentos.
- **Tests:** cálculo del crédito por tramos, acción sin comunicación de inicio (no bonificable), formación de PRL vencida que bloquea el turno, alta reintentada que no duplica el expediente, baja que revoca accesos según checklist.
- **Aceptación:** la formación ejecutada cuadra con su bonificación y el expediente de incorporación es único y auditable.

## Límites de esta fase

No incluye entrevistas por vídeo, evaluación de desempeño con puntuaciones automáticas ni decisiones de promoción. Todo eso requiere revisión específica de uso de IA y queda para una ola posterior, con el mismo criterio: humano decide, sistema documenta.
