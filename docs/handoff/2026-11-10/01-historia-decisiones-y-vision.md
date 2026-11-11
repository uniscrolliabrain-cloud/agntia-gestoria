# 01 · Historia del chat, decisiones del propietario y visión del producto

Fecha de corte: 10 de noviembre de 2026. Documento de relevo para otras IAs. Esta reconstrucción utiliza los mensajes disponibles de esta conversación y la documentación/código del checkout; no pretende recuperar mensajes no suministrados ni respuestas de cuestionario cuyo enunciado no aparece. Distingue deseos, código observado y resultados ejecutados.

## Cómo leer este relevo

El proyecto principal de esta carpeta es `uniscrolliabrain-cloud/agntia-gestoria`. La conversación empezó con otro producto, Agntia-video, que se conserva como antecedente porque explica requisitos compartidos: instalar herramientas en una plataforma TypeScript/Hono/pnpm, permitir que humanos y agentes utilicen las mismas operaciones y mantener una experiencia sencilla. No se deben mezclar sus datos, dependencias o repositorios por compartir filosofía.

La base técnica del middleware está en la rama `feat/odoo-complete-adapter`, PR #4. Al iniciar este relevo su head remoto era `e69bd7facfd54ef37539e34dbac130527bd098e2`; la PR seguía abierta. `main` figuraba en `1fd25d932a26acab0d865aa4aa3d7ed83876282e`. Estos son hechos de un instante, no una garantía del estado que encontrará otra IA. Verificar refs, árbol y cambios locales antes de actuar.

El código principal del adaptador se publicó en `84504053d71c966db58d8de0fdf44b9817ebef82`. Después llegaron documentación de CI, el plan de producto y este relevo. No inventar un SHA distinto para cada campaña cuando varias se implementaron en un lote único.

## Primer producto: edición de podcast con avatares

El propietario pidió un repositorio público llamado Agntia-video para editar podcasts con avatares IA. El material incluye vídeos, audios separados y B-roll. Quería dejar los archivos en una carpeta, construir un briefing conversando con un agente económico como DeepSeek, analizar vídeo con Gemini y seleccionar los mejores momentos conforme a instrucciones. Solicitó Windows y servidor, previsualización antes de exportar, elección de idioma y soporte español, inglés y francés.

Después añadió mejora de voz con IA, incorporación de MP3 y edición al ritmo de beats. Pidió integración en otro repo TypeScript/Hono/pnpm, herramientas para que agentes trabajaran como personas, una interfaz sencilla inspirada en Veed y un chat en columna derecha con adaptación móvil. Algunos mensajes anteriores son respuestas aisladas como «Ambas» o «No»; sin su pregunta no deben convertirse en restricciones inventadas.

En esta sesión se leyó, sin modificarlo, el README local de `/workspace/Agntia-video`. Declara una versión 0.4 con servicio Python/FFmpeg, estudio web, SDK y adaptador Hono, DeepSeek/Gemini opcionales, limpieza RNNoise local, música, beats, subtítulos y clips verticales. Esa lectura acredita lo que declara el documento, no una ejecución nueva de su suite ni el contenido actual de GitHub. Si otra IA retoma vídeo, debe abrir su AGENTS.md, historial y pruebas propios. No trasladar las evidencias de Gestoría al editor.

## Nacimiento de Agntia Gestoría

El propietario cambió el foco a gestión empresarial española. Pidió investigar legislación y repositorios públicos, crear un paquete Python instalable y conectarlo a su plataforma TypeScript para que humanos y agentes puedan prestar servicios de gestoría. Indicó alcance de pymes y autónomos y posibles tributaciones en todo el territorio español.

Quiso declaraciones de renta, IVA e IRPF trimestrales/anuales, procesamiento y almacenamiento de datos, motores deterministas de cálculo, dashboard SaaS, informes, presentaciones e infografías. Esa es la ambición de producto; nunca debe confundirse con cobertura fiscal ya alcanzada. El repositorio actual tiene motores 303/130 muy delimitados para 2026, no una gestoría universal ni renta anual completa.

El repositorio indicado es `uniscrolliabrain-cloud/agntia-gestoria`. El usuario insistió en guardar avances y no perder trabajo, preguntó por main y pidió un handoff extenso para continuar desde su laptop con PowerShell. Estas solicitudes explican la importancia de publicar y señalar exactamente la rama, el commit y la evidencia. Decir «está en el repo» sin indicar si está fusionado resulta insuficiente.

## La campaña Odoo y su evolución

El propietario entregó una campaña extensa C01–C20 basada en un snapshot llamado agntia-gestoria.txt y en Odoo Community19. La campaña exigía cotejar snapshot con main, preservar API/fiscalidad/revisión/auditoría, construir un adaptador seguro, probar contra dos bases y entregar evidencia. Si el snapshot no está disponible no se puede afirmar identidad con él; el baseline real de GitHub sustituye únicamente la referencia operativa disponible.

C01 congeló/inventarió fuentes. C02 auditó archivos concretos de Odoo y fijó upstream. El usuario autorizó fusiones históricas y conservación del handoff en main. Más tarde indicó que se implementaran todas las fases restantes sin esperar a Docker, que ejecutaría con otra IA. Esa instrucción autorizó avanzar el código en lote, pero no transformó gates runtime no ejecutados en PASS ni autorizó producción o cambios en `agente`.

La documentación histórica de C01/C02 puede describir fases no iniciadas. Leer los documentos posteriores y el estado del código para resolver la cronología; no borrar los antecedentes para fabricar una historia lineal. La implementación C03–C20 pertenece a la PR #4 y conserva pendientes de instalación real.

## Corrección fundamental del propietario

El usuario aclaró expresamente: quiere encajar como middleware en Odoo Community que su organización gestiona y autoaloja. Por tanto, Odoo es backend propio, no un producto que el cliente deba contratar o aprender a manejar. AgntiaPro será el acceso del owner y los trabajadores humanos/sintéticos. Gestoría gobierna sus operaciones de dominio y se integra con el ERP.

Esta precisión corrige explicaciones anteriores que parecían proponer un ERP nuevo o comparar el paquete Python aislado con toda la funcionalidad de Holded. Muchas capacidades futuras consisten en instalar/configurar módulos existentes y exponer recorridos controlados. Otras, como nóminas españolas, bancos y fiscalidad, requieren elegir soluciones y validarlas; no están resueltas por instalar cualquier addon.

La visión vigente se desarrolla en el documento raíz `VISION-Y-PLAN-AGNTIA-GESTORIA.md`: ventas, facturación/VERI*FACTU, gastos, banca, contabilidad, impuestos, informes, operaciones y laboral, con fases de producto P0–P8. Es una especificación de futuro, no una activación automática de funciones sensibles.

## Demo, alojamiento y licencias

El propietario decidió realizar la demo gratis en su PC y confirmó que dispone de las herramientas. Puede usar un owner inventado y empresas sintéticas para probar aplicación, aislamiento y procesos locales. Eso no crea por sí solo un tenant AgntiaPro ni autoriza a enviar datos ficticios a producción AEAT.

Se discutieron Fly.io y un VPS como opciones posteriores. No se desplegó en ninguna. Los importes mensuales mencionados fueron estimaciones, no presupuestos vigentes ni gastos contratados. La siguiente IA no debe contratar cloud para hacer funcionar una demo local que el usuario ya decidió ejecutar en su equipo.

La conversación corrigió una ambigüedad sobre licencias: Odoo Community19 utiliza LGPLv3 y no exige suscripción por usuario para este uso. Docker Desktop dispone de condiciones propias de gratuidad, verificadas en fuentes oficiales, que hay que respetar. Enterprise y módulos comerciales no son requisitos implícitos del proyecto. Open source sigue teniendo licencia, obligaciones y mantenimiento.

## Forma de colaborar y límites persistentes

El usuario prefiere acción y continuidad; cuando sea necesaria una aclaración pide preguntas de una en una. No detener trabajo autorizado para pedir permisos rutinarios. Sí conservar las restricciones expresas: no modificar `uniscrolliabrain-cloud/agente`, producción, secretos reales o fórmulas fiscales fuera de su alcance sin la autorización que corresponda. Una aprobación anterior de un merge concreto no permite atribuir todas las futuras fusiones a esa aprobación.

La siguiente IA debe empezar comprobando el checkout, leer el índice de esta carpeta, revisar evidencias y ejecutar el laboratorio que falte. Debe comunicar resultados con precisión, publicar avances revisables y diferenciar preparado, ejecutado, aceptado y presentado. El objetivo es que el propietario dirija su empresa mediante AgntiaPro con trabajo real por detrás; ninguna personalidad de agente, animación o frase de chat sustituye permisos, hechos o justificantes.


## Fuentes internas para continuar

- [Visión detallada acordada](../../../VISION-Y-PLAN-AGNTIA-GESTORIA.md).
- [Handoff de implementación](../../../ODOO-IMPLEMENTATION-HANDOFF.md).

Siguiente lectura: [índice y protocolo de uso](README.md). La evidencia se atribuye al SHA/entorno descrito, no a cualquier checkout posterior.
