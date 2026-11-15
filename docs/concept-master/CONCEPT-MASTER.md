# AGNTIA GESTORÍA — CONCEPT MASTER V1.0
**Fecha:** 2026-11-15 · **Estado:** TARGET_VISION / EVOLUTIVO · **Repositorio:** `uniscrolliabrain-cloud/agntia-gestoria`

> **Visión:** una gestoría empresarial agéntica integral, verificable y territorialmente consciente para autónomos y sociedades españolas: un sistema que entiende la actividad, organiza evidencia, interpreta obligaciones con reglas jurídicas versionadas, prepara cálculos deterministas, coordina revisiones profesionales, ejecuta trámites exclusivamente mediante representación y conectores habilitados, verifica justificantes y mantiene una memoria normativa y operativa auditable.

## 0. Contrato del Concept Master

Este documento define **el producto final al que aspiramos**, no la funcionalidad actualmente implementada. El repositorio ya dispone de una aplicación Python, motores acotados 303/130, cliente TypeScript y laboratorio Odoo; no se atribuye a ese código ninguna capacidad futura por describirla aquí. **No** se acorta el concepto para ajustarlo al estado del software. Su evolución V2 es legítima tras construir o descubrir nuevas posibilidades.

**Etiquetas:** [C] práctica o tecnología existente; [D] diseño propuesto de Agntia; [H] hipótesis que requiere validación. **P0/P1/P2** ordenan la construcción, no limitan la visión. Las reglas jurídicas, plazos, modelos, versiones y administraciones **nunca** se activan basándose solo en un resumen de IA. Toda conclusión tributaria depende de ejercicio, territorio, sujeto, actividad, régimen y hechos probados.

**Principios heredados:** `uniscrolliabrain-cloud/agente` gobierna identidad canónica, LAIA, agentes, políticas transversales, tareas, aprobaciones y eventos. Gestoría posee semántica contable/fiscal/laboral, expedientes, reglas, cálculos y conectores de su dominio. Los twins no se convierten en identidades con autoridad independiente. `LLM propone; reglas y humanos autorizados disponen`.

## 1. Ambición: de gestor documental a sistema operativo de cumplimiento

### 1.1 Problema
Una pyme española gestiona simultáneamente obligaciones mercantiles, contables, fiscales, laborales, societarias y administrativas, distribuidas entre administraciones y calendarios. Las fuentes de datos se repiten; las normas cambian; los trámites pueden exigir representación; los errores generan sanciones, pérdidas de derechos o costes. El usuario necesita un equipo que **comprenda la situación real**, no una lista estática de modelos.

### 1.2 Resultado final
- **Empresa jurídicamente legible:** una representación versionada de quién es, qué hace, dónde opera, con qué regímenes, administraciones y obligaciones.
- **Obligaciones vivas:** detección, calendario, evidencia, preparación, revisión, presentación autorizada, justificante y seguimiento.
- **Contabilidad y fiscalidad explicables:** cálculo reproducible desde documentos y hechos clasificados hasta casillas, asientos y declaraciones.
- **Cierre operativo continuo:** conciliación, alertas, incidencias, subsanaciones, rectificaciones y control de plazos.
- **Servicio profesional aumentado:** colaboración entre owner, gestor, asesor fiscal, laboralista, agente Juan y LAIA, con responsabilidad y firma humanas cuando correspondan.
- **Inteligencia preventiva:** avisos de obligaciones, cambios normativos, riesgos de incoherencia, datos faltantes y oportunidades legítimas sujetas a revisión.
- **Conectividad verificable:** Odoo, bancos, facturación, administraciones y otras especialidades mediante adaptadores de capacidades explícitas.

### 1.3 Diferenciadores [D]
1. **Regulatory Digital Twin:** gemelo normativo de la empresa, condicionado por territorio, ejercicio, régimen, actividad y hechos.
2. **Obligation Graph:** grafo de obligaciones, desencadenantes, excepciones, fechas, dependencias, fuentes y estado.
3. **Legal Rule Compiler:** transformar normas revisadas por expertos en paquetes declarativos versionados y testeables; la IA no promulga reglas.
4. **Evidence-to-Filing Chain:** procedencia desde documento original hasta cálculo, revisión, mandato, transmisión, justificante y estado posterior.
5. **Jurisdiction Router:** identificar competencia, puntos de conexión y administraciones potenciales sin presuponer territorio por domicilio.
6. **Compliance Time Machine:** reconstruir qué normativa, datos y decisiones eran aplicables en una fecha y ejercicio determinados.
7. **Prevention & Remediation Engine:** anticipar incumplimientos y preparar correcciones, sin ejecutarlas sin autoridad.
8. **Professional Review Workspace:** expediente inteligente para humanos con incertidumbres, comparaciones, fuentes y responsabilidad.
9. **Enterprise Obligations Orchestra:** cooperación con Finanzas, RRHH, Legal, Seguros y Ciberseguridad bajo un único propietario de cada efecto.
10. **Regulatory Change Intelligence:** detectar cambios normativos y proponer pruebas de regresión de reglas, nunca autoactivar una reforma por noticia.

## 2. Frontera: normativa, industria, open source e investigación

### 2.1 Referentes de producto (mapa de benchmarking)
**Odoo Community + OCA l10n-spain, ERPNext, FacturaScripts y Dolibarr** están documentados en `docs/repositories.md`. Ampliar comparación a **Sage, Wolters Kluwer a3, Cegid, Holded, Quipu, Declarando, TaxDown, Xolo, DATEV y Avalara** según vertical: contabilidad, asesoría, fiscalidad, colaboración, factura, localización, portales, automatización y cumplimiento. Estos nombres son **candidatos a benchmarking**; sus funciones, precios, cobertura española y APIs deben verificarse por producto y edición, sin atribuir paridad a Agntia.

### 2.2 Open source e infraestructura
- **Odoo Community:** ERP extensible con addons y API según versión/edición. https://github.com/odoo/odoo
- **OCA l10n-spain:** localización española, módulos específicos y comunidad; revisar compatibilidad y licencia por módulo. https://github.com/OCA/l10n-spain
- **FacturaScripts:** referencia para facturación/contabilidad local. https://github.com/NeoRazorX/facturascripts
- **ERPNext:** workflows y contabilidad, localización española no garantizada. https://github.com/frappe/erpnext
- **Dolibarr:** módulos empresariales. https://github.com/Dolibarr/dolibarr
- **OpenFisca:** motor de reglas sociofiscales y modelización normativa, candidato conceptual, no validador fiscal español universal. https://github.com/openfisca/openfisca-core
- **Akoma Ntoso / LegalRuleML:** líneas de representación estructurada de documentos jurídicos y reglas, sujetas a evaluación de compatibilidad y coste. https://www.oasis-open.org/committees/legalruleml/
- **XBRL / iXBRL:** representación y validación de reporting financiero cuando proceda. https://www.xbrl.org/
- **Peppol BIS Billing:** intercambio de facturas estructuradas, solo cuando el régimen y las obligaciones de interoperabilidad lo requieran. https://docs.peppol.eu/poacc/billing/3.0/

**Licencias:** OCA y módulos ERP pueden tener copyleft y condiciones de distribución. No copiar código ni declarar compatibilidad legal por enlazar repositorios. Preferir APIs y adaptadores aislados con evaluación jurídica y de licencias.

### 2.3 Investigación aplicada
- **Knowledge representation & reasoning:** ontologías de sujetos, actividades, hechos, obligaciones, excepciones, administraciones y versiones.
- **Rules-as-code:** reglas ejecutables con precedencia, ámbito, fuentes, vigencia y pruebas.
- **Temporal databases:** tiempo de validez jurídica y tiempo de conocimiento; las normas pueden ser publicadas en una fecha y aplicarse a ejercicios anteriores o posteriores.
- **Formal methods:** propiedades de no duplicación, completitud de estados, invariantes contables y permisos.
- **Information extraction:** OCR/document AI con validación humana, trazabilidad de campos y resistencia a inyección.
- **Legal retrieval:** búsqueda de legislación y jurisprudencia con fecha, jerarquía normativa, consolidación y fuente oficial.
- **Uncertainty-aware reasoning:** distinguir hecho confirmado, dato declarado, clasificación propuesta, interpretación discutida y ausencia de información.
- **Process mining:** detectar cuellos de botella y desviaciones en flujos de expedientes, sin inventar obligaciones.
- **Privacy-preserving learning [H]:** mejora de modelos sin mezclar datos entre clientes, previa justificación legal y evaluación de utilidad.

### 2.4 Fuentes jurídicas prioritarias
BOE y versiones consolidadas; AEAT (sede, instrucciones por ejercicio, calendarios y esquemas); Seguridad Social/TGSS/Sistema RED; SEPE; Registro Mercantil; administraciones autonómicas; haciendas forales de Álava, Bizkaia, Gipuzkoa y Navarra; Agencia Tributaria Canaria; administraciones de Ceuta/Melilla; AEPD; órganos judiciales cuando corresponda. **Una URL o resumen no sustituye la comprobación de vigencia y ámbito en el momento de actuar.**

## 3. Taxonomía de capacidades finales (G01–G78)

### A. Identidad jurídica, empresa y territorio
**G01 [C/P0]** Ficha jurídica y fiscal de persona física, sociedad, representantes, socios, actividades y establecimientos.
**G02 [C/P0]** Registro de hechos económicos/documentos con procedencia, versiones y responsables.
**G03 [D/P1]** Regulatory Digital Twin con regímenes, obligaciones, derechos, permisos y condiciones.
**G04 [D/P1]** Jurisdiction Router: AEAT, forales, Navarra, Canarias, Ceuta/Melilla y otros órganos competentes.
**G05 [C/P1]** Gestión de epígrafes, actividades, censos, altas, modificaciones y bajas con evidencia.
**G06 [D/P1]** Historial temporal de cambios de domicilio, actividad, administración y régimen.
**G07 [C/P2]** Estructuras multiempresa, grupo, establecimiento y operaciones interterritoriales.
**G08 [D/P2]** Mapa de obligaciones dependiente de actividad, hechos y contratos, no solo forma jurídica.

### B. Ingesta, contabilidad y facturación
**G09 [C/P0]** Captura documental, clasificación asistida y revisión de campos críticos.
**G10 [C/P0]** Libro de ingresos, gastos, facturas, retenciones y ajustes con referencias únicas.
**G11 [C/P1]** Integración ERP/Odoo, facturación, bancos y nómina con fuente de autoridad.
**G12 [C/P1]** Conciliación bancaria y documental con excepciones y evidencias.
**G13 [C/P1]** Plan General Contable/PGC PYMES, asientos, libros y cierres según ámbito.
**G14 [C/P1]** Facturación electrónica B2B e interoperabilidad conforme a normas y fechas aplicables.
**G15 [C/P1]** Sistemas informáticos de facturación/VERI*FACTU y regímenes territoriales cuando proceda, sin claims prematuros.
**G16 [C/P2]** Inmovilizado, amortizaciones, provisiones, periodificaciones, existencias y ajustes.
**G17 [D/P2]** Accounting Evidence Graph: asiento→documento→contrato→contraparte→aprobación→norma.
**G18 [C/P2]** Cierre contable y conciliación con Finanzas, manteniendo autoridades diferenciadas.

### C. IVA e imposición indirecta
**G19 [C/P0]** Motores deterministas por modelo, ejercicio, período y régimen; 303 actual como base acotada.
**G20 [C/P1]** 303 completo según supuestos verificados: prorrata, inversiones, rectificaciones y regímenes.
**G21 [C/P1]** 390 y obligaciones informativas relacionadas cuando procedan.
**G22 [C/P1]** 349, intracomunitarias, importaciones, exportaciones y operaciones internacionales según ámbito.
**G23 [C/P1]** Recargo de equivalencia, criterio de caja, inversión de sujeto pasivo y regímenes especiales.
**G24 [C/P2]** OSS/IOSS y comercio transfronterizo cuando corresponda.
**G25 [C/P2]** IGIC, IPSI y reglas indirectas territoriales con motores independientes y validados.
**G26 [D/P2]** Motor de clasificación fiscal explicable que propone y bloquea ante hechos faltantes.
**G27 [D/P2]** Conciliación cruzada de libros, modelos, declaraciones previas y justificantes.

### D. IRPF, retenciones y renta
**G28 [C/P0]** Motor 130 de ámbito admitido y evidencias; base para expansión.
**G29 [C/P1]** 130/131 según regímenes, módulos, estimación directa y excepciones.
**G30 [C/P1]** 111/190, 115/180 y otros modelos de retenciones aplicables.
**G31 [C/P1]** Renta anual modelo 100 con situación personal, familiar y fuentes de renta relevantes.
**G32 [C/P1]** Escalas y deducciones autonómicas/estatales versionadas por ejercicio.
**G33 [C/P2]** Actividades económicas, ganancias patrimoniales, inmuebles y otras rentas conforme a cobertura validada.
**G34 [D/P2]** Comparación de opciones fiscales legales con restricciones y revisión profesional.
**G35 [D/P2]** Reconstrucción de decisiones de clasificación y rectificaciones por ejercicio.

### E. Sociedades y mercantil
**G36 [C/P1]** Impuesto sobre Sociedades 200/202, ajustes, bases negativas y regímenes admitidos.
**G37 [C/P1]** Cierre, formulación, aprobación y depósito de cuentas anuales con calendario.
**G38 [C/P1]** Libros mercantiles, legalización, actas, poderes y expedientes societarios.
**G39 [C/P2]** Operaciones societarias, administradores, participaciones y cambios registrales.
**G40 [C/P2]** Conciliación fiscal-contable, diferencias temporarias/permanentes y trazabilidad.
**G41 [D/P2]** Corporate Compliance Graph con hitos, dependencias y responsables.
**G42 [D/P2]** Simulaciones de reorganización y estructura con asesoramiento profesional, sin decisiones automáticas.

### F. Laboral, nómina y seguridad social
**G43 [C/P1]** Expedientes de alta, baja, variación, contratación y representación.
**G44 [C/P1]** Calendario laboral, convenios, jornadas, ausencias, permisos y vacaciones.
**G45 [C/P1]** Nómina, cotizaciones y retenciones mediante motores o proveedores validados.
**G46 [C/P1]** Sistema RED/TGSS/SEPE con credenciales y autorización adecuadas.
**G47 [C/P2]** Finiquitos, indemnizaciones, ERTE y situaciones complejas bajo revisión laboral.
**G48 [C/P2]** PRL, formación obligatoria y documentación según ámbito.
**G49 [D/P2]** Labor Compliance Graph y simulación de costes/obligaciones.
**G50 [D/P2]** Coordinación con RRHH y Finanzas para costes, planificación y límites de decisión automatizada.

### G. Obligaciones, representación y tramitación
**G51 [D/P0]** Obligation Graph con desencadenantes, excepciones, fechas, administración y evidencias.
**G52 [C/P0]** Expediente versionado: datos, documentos, revisión, cálculo y estado.
**G53 [C/P1]** Calendario oficial versionado, festivos, domiciliación y cambios de plazo.
**G54 [C/P1]** Revisión profesional de casillas, hechos, criterios y fuentes.
**G55 [C/P1]** Representación, apoderamientos, certificados y colaboración social verificables.
**G56 [C/P1]** Presentación electrónica autorizada por conector oficial y ámbito habilitado.
**G57 [C/P1]** Justificante auténtico, CSV/verificación, acuse, liquidación y reconciliación.
**G58 [C/P2]** Complementarias, rectificativas, requerimientos, recursos y subsanaciones.
**G59 [D/P2]** Evidence-to-Filing Chain reproducible con estados jurídicos y técnicos separados.
**G60 [D/P2]** Compliance Time Machine para reconstruir expedientes con normativa vigente entonces.

### H. Inteligencia normativa, prevención y asesoramiento
**G61 [D/P1]** Catálogo normativo versionado con jerarquía, ámbito y vigencia.
**G62 [D/P1]** Legal Rule Compiler con revisión experta y fixtures antes de activar.
**G63 [D/P1]** Regulatory Change Intelligence: detección, análisis de impacto y propuesta de migración.
**G64 [D/P1]** Motor de preguntas sobre hechos faltantes y conflictos de evidencia.
**G65 [D/P2]** Prevention & Remediation Engine: riesgo de incumplimiento y acciones revisables.
**G66 [D/P2]** Asesoramiento explicable con alternativas y fuente; distinguir información, cálculo y criterio profesional.
**G67 [H/P2]** Detección automática de inconsistencias normativas entre administraciones con revisión experta.
**G68 [H/P2]** Formalización verificable de reglas fiscales complejas con pruebas de propiedades y contraejemplos.

### I. Agentes, UX, plataforma y aprendizaje
**G69 [D/P0]** Juan especialista de Gestoría, LAIA supervisora y twins por tenant bajo mandato.
**G70 [D/P1]** Portal owner/asesor: bandeja de obligaciones, documentos, expedientes y decisiones.
**G71 [D/P1]** Copiloto de revisión: diferencias, casillas, fuentes, supuestos y preguntas pendientes.
**G72 [D/P1]** Workflows deterministas, outbox, reconciliación, idempotencia y auditoría.
**G73 [D/P1]** Interoperabilidad con Odoo, Finanzas, Legal, RRHH, Seguros y Ciberseguridad.
**G74 [D/P1]** Informes PDF, paneles, alertas y briefing diario/semanal/mensual con trazabilidad.
**G75 [D/P2]** Sesiones de voz/avatar Anam opcionales, sin sustituir firma o autenticación fuerte.
**G76 [D/P2]** Memoria de expedientes y precedentes internos por empresa con control de vigencia.
**G77 [D/P2]** Evaluación continua de exactitud normativa, casos adversariales y drift de reglas.
**G78 [H/P2]** Benchmarking agregado de procesos con privacidad demostrable y base jurídica específica.

## 4. Arquitectura conceptual de destino

### 4.1 Planos
1. **Identity & Authority:** tenant, empresa, persona, actor, representación, mandatos y permisos.
2. **Evidence & Document:** documentos, OCR, procedencia, versiones, integridad, archivo y retención.
3. **Business Semantics:** sujetos, actividad, establecimientos, operaciones, libros y hechos económicos.
4. **Regulatory Knowledge:** fuentes oficiales, normas, artículos, vigencias, territorios, interpretaciones y reglas aprobadas.
5. **Deterministic Engines:** contabilidad, fiscalidad, laboral, calendarios, fórmulas, validaciones y excepciones.
6. **Case & Filing:** expedientes, revisión, firmas, autorizaciones, transmisión, justificantes y rectificación.
7. **Agent & Experience:** Juan, LAIA, especialistas, workspaces, alertas y colaboración.
8. **Governance & Integration:** Odoo/ERP, administraciones, otros repos, audit, outbox, seguridad y observabilidad.

### 4.2 Pipeline canónico
`fuente/documento → ingestión y procedencia → extracción propuesta → revisión de hechos → determinación de jurisdicción y régimen → selección de reglas vigentes → cálculo determinista → validación de ámbito/completitud → expediente versionado → revisión humana competente → representación/consentimiento y aprobación → transmisión oficial autorizada → justificante verificable → conciliación de estado → archivo y seguimiento`.

**Invariantes:**
- Un documento extraído no es un hecho fiscal confirmado.
- Una suma correcta no prueba deducibilidad ni adecuación contable.
- Un modelo listado no es un modelo implementado.
- Un expediente aprobado no está presentado.
- Un HTTP 200 del conector no basta: exigir justificante y estado oficial según trámite.
- Un timeout tras transmisión no autoriza repetir el envío sin reconciliación.
- Una regla de territorio común no se extrapola a Canarias, forales, Ceuta/Melilla o situaciones mixtas.
- Un LLM no cambia reglas fiscales en producción ni decide competencias.
- Un agente no firma, representa ni ejerce competencias profesionales por simular una identidad humana.
- La ausencia de un dato no implica exención, tipo cero ni falta de obligación.

### 4.3 Entidades de dominio
`Tenant, LegalSubject, Company, Activity, Establishment, FiscalDomicile, TaxRegime, Jurisdiction, Administration, CompetenceAssessment, RepresentationMandate, ProfessionalReviewer, SourceDocument, ExtractedField, VerifiedFact, EconomicRecord, LedgerEntry, TaxClassification, LegalSource, NormVersion, RulePackage, RuleDecision, Obligation, ObligationTrigger, CalendarEntry, FilingCase, CalculationRun, BoxResult, ReviewDecision, ApprovalBinding, SubmissionIntent, ExternalReceipt, OfficialAcknowledgement, RectificationCase, ReconciliationState, AuditEvent, AuthorityMap, TwinBinding`.

**Temporalidad bitemporal:** `validFrom/validTo` (vigencia jurídica) y `recordedAt/supersededAt` (conocimiento del sistema). Reglas de retroactividad y disposiciones transitorias explícitas; no inferir vigencia de una fecha de descarga. Cada cálculo guarda `rulePackageHash, sourceRefs, factsSnapshotHash, model/year/period/jurisdiction, roundingPolicy, reviewer, outputHash`.

### 4.4 Motor normativo
Compilar normas **revisadas** a un DSL tipado:
`Rule = {authority, legalBasis, jurisdiction, taxOrProcedure, subjectType, period, effectiveRange, preconditions, exclusions, requiredFacts, calculation, rounding, evidence, reviewStatus, tests}`.
Evaluación con tres estados `APPLICABLE | NOT_APPLICABLE | INDETERMINATE`; no convertir UNKNOWN en false. Conflictos entre normas generan `BLOCKED_REVIEW`, no selección heurística silenciosa. Cada paquete tiene casos de referencia oficiales, límites, exclusiones y regresión entre ejercicios. IA propone borradores de reglas, **jamás los activa**.

### 4.5 Motor de estados del expediente
`DISCOVERED → EVIDENCE_PENDING → FACTS_VERIFIED → SCOPE_VALIDATED → CALCULATED → READY_FOR_REVIEW → REVIEWED → AUTHORIZED → SUBMISSION_PENDING → SUBMITTED_UNCONFIRMED → OFFICIALLY_ACCEPTED | OFFICIALLY_REJECTED | OUTCOME_UNKNOWN → RECONCILED`.
Estados alternativos: `BLOCKED_SCOPE, BLOCKED_REPRESENTATION, BLOCKED_RULE_VERSION, NEEDS_RECTIFICATION, SUPERSEDED, CANCELLED`. `OFFICIALLY_ACCEPTED` solo con evidencia administrativa válida; aceptación técnica y efectos jurídicos pueden diferir según procedimiento.

## 5. Especialización territorial española

**Territorio común:** AEAT y normativa estatal/autonómica según tributo. **Canarias:** IGIC, REF y especificidades, sin deducir por residencia una exención general. **País Vasco:** Concierto Económico y administraciones forales Álava, Bizkaia y Gipuzkoa, con puntos de conexión por impuesto. **Navarra:** Convenio Económico y competencia según supuestos. **Ceuta/Melilla:** IPSI y reglas locales. **Sociedades multi-territorio:** reparto, volumen de operaciones, competencia y comprobaciones por período. **Laboral:** convenio, sector, territorio y régimen de cotización.

El Jurisdiction Router entrega `possibleAuthorities, governingRules, decisiveFacts, evidence, conflicts, unresolvedQuestions`. Si no puede determinar la competencia, bloquea el trámite y solicita revisión. La clasificación de una operación se separa de la administración competente y del órgano de presentación.

## 6. Interacción entre agentes y repositorios

**Roles funcionales:** Juan (gestoría), asesor fiscal, controller contable, técnico laboral, especialista en obligaciones, gestor documental y revisor de cumplimiento. Son perfiles de SOPs/capacidades y twins, no personas autónomas con poder legal. LAIA supervisa y presenta el estado al owner.

**Cooperación:**
- **Finanzas:** caja, presupuestos, escenarios y obligaciones económicas; Gestoría conserva autoridad sobre reglas y cálculos fiscales.
- **Legal:** interpretación jurídica compleja, contratos, representación y litigios; delimitación por expediente.
- **RRHH/Formación:** hechos laborales, nómina, convenios, formación y obligaciones; evitar duplicar efectos.
- **Ventas/Clientes:** facturas, ingresos, contrapartes y documentos comerciales con conciliación.
- **Seguros:** obligaciones, primas, siniestros y contingencias.
- **Ciberseguridad:** protección de datos fiscales, fraude documental, credenciales, integridad y continuidad.
- **Comunicación:** notificaciones a clientes y autoridades únicamente mediante canales autorizados.
- **Odoo:** autoridad de objetos ERP según binding; Gestoría conserva proyecciones, verificaciones y expedientes.

**Tooling propuesto:** `gestoria.company.profile.read`, `gestoria.obligations.list`, `gestoria.document.classify.propose`, `gestoria.tax.scope.evaluate`, `gestoria.tax.calculate`, `gestoria.case.prepare`, `gestoria.case.diff`, `gestoria.rule.source.explain`, `gestoria.representation.status`, `gestoria.filing.preview`, `gestoria.filing.status`. Preparar una intención de presentación no equivale a transmitir. Las tools no reciben tenant ni permisos libres del LLM; el servidor resuelve identidad y policy.

## 7. UX: gestoría conversable y auditable

**Owner:** «¿Qué tengo que presentar este mes?», «¿Por qué sale este IVA?», «¿Qué documento falta?», «¿Cómo afecta contratar a alguien?», «¿Qué diferencia hay entre lo calculado y lo presentado?», «¿Qué cambios normativos nos afectan?». Respuestas con fuente, fecha, administración, cobertura y preguntas faltantes.

**Workspaces:** Obligation Radar, Company & Jurisdiction Profile, Document Inbox, Accounting Desk, Tax Engine Studio, Filing Case Board, Labor Desk, Corporate Calendar, Regulatory Observatory, Professional Review, Evidence Explorer, Agent Office y Report Factory.

**Interacciones:** casillas navegables hasta registro y documento; diff entre reglas de dos ejercicios; timeline de cambios normativos; matriz de administración/competencia; preguntas para hechos faltantes; bloqueo claro de régimen excluido; comparación de declaración preparada y justificante; alertas de caducidad de representación; revisión profesional con firma/identidad real según necesidad; exportaciones reproducibles. Anam/voz opcional y subordinado a la misma política; «sí» hablado no sustituye una firma o representación legal.

## 8. Seguridad, regulación y responsabilidad profesional

Evaluar RGPD/LOPDGDD, secreto profesional, LGT y conservación, normativa contable/mercantil, servicios de asesoría, prevención de blanqueo cuando proceda, eIDAS, normativa de firma y representación, requisitos de proveedores, normas laborales y AI Act según uso concreto. No afirmar habilitación de colaboración social, certificado, licencia, sistema RED ni conectores oficiales sin verificarlos. Revisar normas y calendarios al momento de activación: **las fechas normativas documentadas en 2026 pueden cambiar**.

**Controles:** tenant isolation en API/DB/workers/archivos/exportaciones; acceso mínimo por empresa y expediente; secretos fuera del LLM; cifrado de originales y backups; rotación y recuperación de claves; audit append-only con integridad externa cuando corresponda; inyección desde PDFs y facturas; datos de salud/laborales con protección reforzada; revisión humana; dual control para trámites críticos; idempotencia y reconciliación de presentaciones; recuperación de desastre; conservación por clase documental y obligación; portabilidad y borrado condicionado por bases legales.

**Autonomía graduada:** L0 leer, L1 clasificar/proponer, L2 calcular reglas validadas, L3 preparar expediente, L4 revisión y aprobación humanas, L5 transmisión oficial solo con representación, credenciales, conector, mandato y controles específicos. La IA no puede autoascender de nivel.

## 9. Pruebas de excelencia y falsación

**Exactitud:** fixtures oficiales por modelo/ejercicio/régimen/territorio, casos límite, rectificativas, redondeo, arrastre de saldos y exclusiones. **Temporalidad:** norma publicada después, retroactividad, cambio de administración y calendario. **Integridad:** documento modificado tras cálculo, asiento equilibrado pero fiscalmente incorrecto, factura duplicada, dato faltante. **Representación:** poder revocado, certificado caducado, mandato insuficiente. **Efectos:** timeout tras transmisión, justificante tardío, rechazo oficial, reintento concurrente. **Tenancy:** dos empresas con identificadores remotos similares, actor delegado, acceso a adjuntos y exportaciones. **Laboral:** convenio incorrecto, jornada, nómina y datos especialmente protegidos. **Seguridad:** prompt injection en documento, OCR manipulado, reglas normativas envenenadas y exfiltración.

**Métricas:** cobertura de obligaciones con verdad de referencia, errores de clasificación, exactitud por casilla, bloqueos correctos, completitud de expedientes, tasa de presentaciones con justificante, duplicados remotos, cumplimiento de plazos, tiempo de revisión profesional, falsos avisos, p95, coste por trámite, recuperación y cero fugas entre tenants. No confundir «0 errores detectados» con ausencia de errores reales.

## 10. Ruta de convergencia

**G0 — Concept & Regulatory Atlas:** fichas G01–G78, taxonomía, ADRs, fuentes por administración, benchmarking y modelo de responsabilidad.
**G1 — Evidence Foundation:** identidad, documentos, OCR revisable, hechos, temporalidad, representación, tenant y seguridad.
**G2 — Accounting & ERP:** Odoo Community, contabilidad, facturación, conciliación, inmutabilidad lógica y contratos.
**G3 — Rule Compiler:** DSL, paquetes normativos, versionado, fixtures oficiales, revisión y regresión.
**G4 — Fiscal Expansion:** 303/130 extendidos, retenciones, renta, sociedades, IGIC/IPSI/forales por módulos verificados.
**G5 — Filing & Receipts:** autorizaciones, conectores oficiales, firma/representación, estados, justificantes y rectificaciones.
**G6 — Labor & Corporate:** nómina, Seguridad Social, SEPE, mercantil y calendarios.
**G7 — Agentic Gestoría Office:** Juan, LAIA, workspaces, SOPs, memoria y coordinación inter-repos.
**G8 — Regulatory Intelligence:** cambios normativos, impacto, prevención, pruebas y mejoras propuestas.
**G9 — Concept V2:** revisión de frontera tras datos reales, evolución legal y aprendizaje de ingeniería.

**Gates:** cada regla solo entra con fuente oficial vigente, ámbito explícito, pruebas, revisión y rollback. Cada efecto externo requiere identidad, autoridad, aprobación, receipt y reconciliación. No se despliega sin aprobación del founder.

## 11. Hipótesis y preguntas abiertas

1. ¿Qué parte del conocimiento normativo español puede formalizarse de modo mantenible y qué parte requiere interpretación profesional continua? [H]
2. ¿Cómo medir cobertura de obligaciones cuando faltan hechos y la empresa no sabe que faltan? [H]
3. ¿Qué formatos y vías de presentación oficiales son técnicamente accesibles por modelo, ejercicio y administración? [D]
4. ¿Qué competencias profesionales, representación y controles AML corresponden al modelo comercial concreto? [D]
5. ¿Qué grado de integración Odoo 19 es sostenible ante actualizaciones y cambios de módulos? [D]
6. ¿Qué ontología permite unificar AEAT, haciendas forales, IGIC y laboral sin perder semántica? [H]
7. ¿Qué beneficios reales aporta un compilador de reglas frente a motores especializados escritos a mano? [H]
8. ¿Cómo detectar normas modificadas con vigencia retroactiva y regenerar expedientes afectados sin alterar justificantes históricos? [D]
9. ¿Cómo evitar errores por automatización en situaciones personales sensibles de IRPF y laboral? [D]
10. ¿Qué controles permiten a un asesor humano revisar cientos de expedientes sin crear falsa sensación de seguridad? [H]
11. ¿Cómo asegurar que los datos ERP importados son completos y fieles, no solo consistentes? [H]
12. ¿Cuáles son las fronteras de autoridad entre Gestoría, Finanzas, Legal y RRHH para cada efecto? [D]

Cada pregunta requiere protocolo de investigación, responsable, fuente, prueba de cierre y decisión versionada. Las hipótesis no demostradas no se presentan como capacidades ya verificadas.

## 12. Fuentes y alcance de la revisión

### Documentación del repositorio inspeccionada
- [README](../../README.md)
- [Ámbito de producto](../product-scope.md)
- [Motores 303/130](../calculation-engines.md)
- [Investigación normativa](../legal-research.md)
- [Repositorios estudiados](../repositories.md)
- [Integración Agente/Odoo](../agente-integration.md)
- [Operación Odoo](../odoo-adapter/operations.md)
- [Plan RRHH](../rrhh/README.md)

### Fuentes normativas primarias y estándares de referencia
- BOE, Ley General Tributaria: https://www.boe.es/buscar/act.php?id=BOE-A-2003-23186
- BOE, Ley del IVA: https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740
- BOE, Ley IRPF: https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764
- BOE, Ley Impuesto sobre Sociedades: https://www.boe.es/buscar/act.php?id=BOE-A-2014-12328
- AEAT, sede electrónica: https://sede.agenciatributaria.gob.es/
- Seguridad Social: https://www.seg-social.es/
- BOE, Concierto Económico: https://www.boe.es/buscar/act.php?id=BOE-A-2002-9969
- BOE, Convenio Económico Navarra: https://www.boe.es/buscar/act.php?id=BOE-A-1990-31117
- BOE, IGIC/REF: https://www.boe.es/buscar/act.php?id=BOE-A-1991-14463
- BOE, IPSI: https://www.boe.es/buscar/act.php?id=BOE-A-1991-7645
- BOE, LSC: https://www.boe.es/buscar/act.php?id=BOE-A-2010-10544
- BOE, Código de Comercio: https://www.boe.es/buscar/act.php?id=BOE-A-1885-6627
- RGPD: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- OCA l10n-spain: https://github.com/OCA/l10n-spain
- OpenFisca: https://github.com/openfisca/openfisca-core
- LegalRuleML: https://www.oasis-open.org/committees/legalruleml/
- Peppol BIS Billing: https://docs.peppol.eu/poacc/billing/3.0/

**Límite:** investigación conceptual selectiva apoyada en documentación ya existente y referencias técnicas/jurídicas. No es una auditoría normativa integral por todos los modelos y ejercicios, ni consulta profesional, ni verificación en vivo de cada API administrativa. Antes de activar reglas, verificar fuentes oficiales actualizadas, vigencia, jurisdicción y cobertura. El Concept Master es una **visión de destino versionable**, no una certificación de cumplimiento.

## 13. Evolución del concepto

`CONCEPT-MASTER.md` es la referencia de diseño de destino. Las versiones V1.x amplían fichas, investigación, pruebas y ADRs; una V2 puede rediseñar capacidades tras nueva ciencia, regulación o experiencia. No eliminar el pasado ni cambiar silenciosamente reglas. La ingeniería persigue el concepto; el concepto no se reduce para justificar el estado del código.
