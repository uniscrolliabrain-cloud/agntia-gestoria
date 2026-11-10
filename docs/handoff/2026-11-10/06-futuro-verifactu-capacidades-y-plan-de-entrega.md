# 06 · Futuro del producto, VERI*FACTU y plan de entrega para otras IAs

Fecha: 10 de noviembre de2026. Este documento recoge los objetivos futuros de la conversación y convierte la comparación con Holded/Odoo en trabajo concreto. Es planificación, no evidencia de implementación, aprobación de producción ni una ampliación automática de los permisos actuales. La especificación extensa de referencia es `VISION-Y-PLAN-AGNTIA-GESTORIA.md`, en la raíz.

## La ambición y el punto de partida

El propietario quiere que su empresa pueda gestionar pymes y autónomos desde AgntiaPro mediante humanos y agentes, usando su Odoo Community autoalojado como backend. La experiencia debería cubrir presupuestos, ventas, facturas, gastos, bancos, contabilidad, impuestos, informes y, progresivamente, operaciones sectoriales y laboral. No desea construir otro ERP ni obligar al cliente a usar Odoo como interfaz principal.

Su observación de que no parece tan lejano es correcta en un sentido importante: CRM, ventas, compras, inventario, fabricación y proyectos ya tienen módulos públicos. Buena parte del esfuerzo es instalar/configurar, exponer operaciones de negocio y conectar una experiencia común. No presentar cada fila de una tabla de funciones como si necesitáramos programar un motor desde cero.

Sin embargo, la existencia de un módulo no demuestra instalación, licencia compatible, mantenimiento para nuestra versión, adaptación española o un proceso agéntico seguro. La distancia real se medirá cerrando recorridos con errores y recuperación, no acumulando addons o calculando un porcentaje de cobertura sin base.

## Holded como referencia de experiencia

Se consultaron el catálogo de funciones y la documentación oficial de impuestos/nóminas de Holded. Describen facturación, gastos/OCR, bancos y conciliación, contabilidad, modelos, CRM, inventario, proyectos, RR.HH. y un complemento de nóminas. Las funciones dependen del plan/complementos y su disponibilidad puede cambiar; comprobar el catálogo antes de una comparación comercial.

La documentación de impuestos distingue presentación de ciertos modelos y no promete cobertura total de todos los territorios; por ejemplo indicaba ausencia de modelos canarios420/425. Por tanto, ni Holded debe describirse como una gestoría universal ni nuestro motor303/130 como equivalente a toda su operativa. La referencia útil es poder completar una tarea de empresa con pocos pasos y resultados verificables.

También hay que distinguir Odoo Community de Enterprise. El core tiene modelos contables y módulos de negocio; determinadas interfaces, informes o automatizaciones requieren evaluar addons adicionales. Revisar OCA/account-financial-reporting y OCA/l10n-spain por versión y licencia, sin instalar indiscriminadamente. Comprar Enterprise no es el supuesto por defecto para cubrir cada hueco.

## Primer recorrido comercial completo

El próximo gran resultado observable debería ser: contacto → oportunidad → presupuesto → revisión/autorización de envío → aceptación → pedido → factura → seguimiento de cobro. Actualmente el adaptador cubre contactos y propuestas de borrador, no todo este circuito.

Cada transición necesita un contrato cerrado. Preparar un presupuesto y enviarlo son acciones distintas; aceptar un comentario ambiguo del chat no acredita aceptación comercial. Deben mantenerse destinatario, importes, líneas, condiciones, impuestos y revisión. Editar el contenido invalida la aprobación ligada al hash anterior.

Odoo aporta los documentos y reglas comerciales. Agntia aporta principal/tenant, propuestas, política, tareas, evidencia, herramientas y pantalla. Humanos y agentes pueden utilizar las mismas operaciones con permisos distintos. No ofrecer model/method libres para que el LLM invente cómo completar un recorrido.

## VERI*FACTU como ampliación prioritaria

El usuario destacó expresamente su importancia. La investigación encontró el módulo público `l10n_es_edi_verifactu` en Odoo19, licencia LGPL-3, dependencias l10n_es y certificate y configuración de pruebas/producción. También se inspeccionó código que usa certificado y endpoints AEAT. Esto demuestra una base técnica candidata; no que esté instalado en nuestro laboratorio ni certificado nuestro producto integrado.

El objetivo es que el agente prepare, el humano autorice, Odoo emita mediante un proceso validado y el middleware conserve seguimiento/evidencias que AgntiaPro muestre al cliente. Necesitamos capturar registro fiscal, hash/encadenamiento, QR y estados/respuestas aplicables. Hay que gestionar rechazo, incidencia, recuperación e incertidumbre conforme al servicio oficial, sin repetir emisión por un timeout.

La emisión de factura, anulación de registro y factura rectificativa son procesos diferentes. No borrar un movimiento emitido para «arreglarlo». La cuenta de integración actual tiene prohibido postear; se necesita diseñar una capacidad específica futura con aprobación y controles, y autorizar ese cambio de alcance antes de activarlo. Esta documentación no concede ese permiso.

La API key Odoo, el firmante HMAC de nuestras aprobaciones y el certificado electrónico tributario tienen funciones distintas. Si remitimos por terceros habrá que verificar representación. Un owner/NIF demo inventado sirve localmente, no reemplaza un certificado/identificación válidos para servicios externos. El laboratorio y preproducción deben quedar separados de producción AEAT por configuración y controles claros.

La AEAT exige declaración responsable del productor para el SIF/versión; no existe una homologación previa automática del software por instalar un addon. Determinar quién asume responsabilidad sobre nuestras modificaciones y la combinación entregada. Los plazos regulatorios se consultaron en fuentes oficiales durante el chat, pero deben revalidarse en BOE/AEAT al implementar; evitar fijar fechas legales como constantes eternas en código.

VERI*FACTU no presenta303/130 ni sustituye factura electrónicaB2B. Tampoco cubre automáticamente TicketBAI o regímenes forales. La matriz por empresa debe decidir qué procedimiento aplica y bloquear el resto. Tener IGIC en una línea es insuficiente para declarar completa la cobertura de Canarias.

## Gastos, bancos y tesorería

El recorrido de gasto necesita documento recibido, extracción, identificación de proveedor, detección de duplicado, cotejo con pedido/recepción, propuesta de clasificación, revisión, registro y seguimiento de vencimiento. Elegir OCR/proveedor/modelo con límites de coste y privacidad. Una confianza alta de extracción no demuestra deducibilidad ni autenticidad.

Los bancos requieren importación de extractos o proveedor autorizado, consentimientos y cobertura real. Empezar con lectura y propuestas de matching, después conciliación autorizada. Los pagos, transferencias y domiciliaciones son otra capacidad sensible, no una consecuencia automática de tener account.payment disponible. Un fichero SEPA generado no acredita pago ejecutado.

La previsión de caja debe distinguir saldo confirmado, cobros esperados, pagos comprometidos y escenarios. No sumar ventas como dinero disponible. Probar pagos parciales, comisiones, devoluciones, duplicados y desconexión/revocación antes de ofrecer automatización a clientes.

## Contabilidad y fiscalidad ampliada

Aprovechar el ERP para plan de cuentas, diarios, apuntes y movimientos. Evaluar módulos para mayor, balances, pérdidas/ganancias, activos, amortizaciones, bloqueo de periodos y cierre. Los informes deben conciliar con el backend y mostrar provisional/revisado/cerrado. Equilibrio debe/haber no demuestra corrección contable.

El avance fiscal debe ser por modelo, ejercicio, régimen y territorio. Primero completar perfiles concretos de autónomo/SL de territorio común; ampliar casos y resúmenes, sociedades y renta anual mediante proyectos verificables. La renta personal incluye datos fuera de la actividad empresarial: no inventar un modelo100 completo leyendo facturas.

Preparar casillas, generar un archivo y presentar son capacidades separadas. La presentación necesita autorización, representación, certificado y justificante oficial conservado. Los futuros agentes pueden explicar fuentes y pendientes; no adquieren representación legal por tener nombre de gestor. Debe distinguirse software de asistencia del servicio profesional efectivamente prestado cuando corresponda.

## Operaciones sectoriales, equipo y laboral

Inventario, fabricación, proyectos, ecommerce/TPV se activarán según el sector piloto. Un autónomo de servicios no necesita fabricar, y una tienda necesita movimientos de stock correctos antes de informes vistosos. El middleware debe vincular pedido, recepción, entrega y factura, con unidades, cantidades, compañía y revisión controladas.

Proyectos requiere horas/costes fiables para medir rentabilidad y distinguir terminado, facturado y cobrado. Las correcciones no deben editar cantidades sin su movimiento o evidencia. Aplicar el mismo patrón de propuesta, aprobación, ejecución y reconciliación donde haya efectos operativos.

En laboral, separar empleados/ausencias/vacaciones de nómina española. Elegir un motor/proveedor mantenido para contratos, convenios, cotización, IRPF, complementos y particularidades. Generar ficheros para SILTRA/RED no equivale a presentarlos ni a recibir aceptación. Los scopes personales deben impedir que un agente financiero lea datos laborales sin necesidad y autorización.

## Hoja de ruta P0–P8

P0 valida el laboratorio real y corrige ORM/ACL, aislamiento, replays y backup. P1 establece catálogo de módulos y onboarding por perfil. P2 cierra ventas/facturación y VERI*FACTU en pruebas con el nuevo alcance autorizado. P3 incorpora gastos/bancos y conciliación propuesta. P4 completa contabilidad y cierre con informes reconciliados.

P5 amplía fiscalidad de forma versionada y trata presentación separadamente. P6 integra operaciones sectoriales necesarias para clientes concretos. P7 desarrolla laboral mediante solución validada. P8 consolida AgntiaPro, runtime, SOP, supervisión, soporte y operación del servicio. La UX y seguridad atraviesan todas las fases; no se dejan para el final por tener una fase de consolidación.

Estas fases no renumeran ni anulan C01–C20: aquellas documentaban el adaptador inicial y sus gates técnicos. P0 usa sus scripts y evidencia y completa lo que aún figura NOT VERIFIED. No atribuir una nueva aprobación a una fase solo porque el usuario pidió una visión de futuro detallada.

## Definición de entrega y próximos trabajos

Por capacidad: identificar módulo/version/licencia, fuente de verdad, entradas, exclusiones, contratos, permisos, propuesta/diff, claves, errores, recuperación, pantalla humana y herramienta agéntica. Ejecutar unitarias relevantes, contratos con proveedor y E2E sintético, y entregar evidencia sanitizada. Habilitar por empresa solo tras aceptación del alcance correspondiente.

La próxima IA no debe empezar por otra tabla abstracta: debe comprobar checkout y completar P0 en el PC. Después, demostrar una venta con datos ficticios desde AgntiaPro o un consumidor servidor autorizado. Medir esfuerzo real de ese patrón para estimar los siguientes dominios, sin prometer plazos o paridad total con Holded que no se han medido.

Fuentes para revalidación: catálogo/Academy de Holded; código19 de Odoo; manifiesto de l10n_es_edi_verifactu; OCA por módulo; AEAT información técnica, pruebas y declaración responsable; BOE RD1007/2023 y modificaciones. Los enlaces se conservan en el plan raíz. El valor esperado es dirigir trabajo empresarial real mediante AgntiaPro; los LLM proponen y explican, mientras el sistema autorizado decide qué puede ejecutarse y conserva lo que realmente ocurrió.


## Fuentes internas para continuar

- [Plan de producto completo](../../../VISION-Y-PLAN-AGNTIA-GESTORIA.md).
- [Compatibilidad y licencias](../../odoo-adapter/COMPATIBILITY.md).
- [Estado de campañas](../../odoo-adapter/final-report.md).

Siguiente lectura: [índice y protocolo de uso](README.md). La evidencia se atribuye al SHA/entorno descrito, no a cualquier checkout posterior.
