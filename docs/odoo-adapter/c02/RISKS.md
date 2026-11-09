# Riesgos y bloqueos C02

1. La imagen nightly y el commit de referencia no tienen equivalencia demostrada; no afirmar que se está probando el mismo código.
2. Las reglas de partners permiten compartidos y excepciones de usuarios internos; compañía permitida por Odoo no equivale a binding autorizado por Gestoría.
3. account.account usa company_ids; una implementación con company_id singular sería errónea.
4. invoice_line_ids incluye secciones/notas; line_ids incluye contrapartidas y cuotas. No sumar sin clasificación y conciliación.
5. Un porcentaje no identifica la naturaleza fiscal del impuesto. Mod420 en un manifiesto tampoco prueba cobertura IGIC.
6. El bot, sus grupos, fields_get y módulos instalados no se han probado. Todas las capacidades remotas permanecen deshabilitadas.
7. Docker local sin acceso efectivo; el entorno estuvo temporalmente indisponible. El intento de obtener permiso no se ejecutó. No ampliar privilegios, usar superuser o desplegar otro host para ocultar el bloqueo.
8. Las 38 comprobaciones estáticas no cumplen por sí solas el gate de integración real. La PR se entrega como borrador y no debe fusionarse como C02 aprobada.
