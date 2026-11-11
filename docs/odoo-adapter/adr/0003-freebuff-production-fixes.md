# ADR 0003 · Correcciones de la entrega Freebuff

El propietario autorizó el 11 de noviembre de 2026 aplicar las correcciones en la rama Freebuff, validarlas e integrar el resultado en main.

El guardado comprueba empresa y clase del objeto, valida IDs y actualiza la clave única cuando se proporciona una nueva. Los tests cubren la preservación del objeto de otra empresa. La política de inventario permite revisar este cambio concreto de storage mediante hashes exactos. Las fórmulas y fuentes fiscales conservan su protección.

El acceso local de propietario necesita configuración explícita. Las sesiones del navegador tienen identificadores opacos persistidos por hash, caducidad y revocación. El origen público se configura en servidor y el login limita intentos por cliente. La protección de cierre humano se aplica en API, interfaz y catálogo del SDK.

Los fallos SQLite al guardar métricas se registran sin sustituir el resultado del proveedor. La incertidumbre determina la acción de reconciliación y el SDK conserva los campos públicos del contrato. La retención clasifica las operaciones persistidas y conserva la identidad de claves antiguas.

La infraestructura fija data_dir en el volumen que respalda el filestore. CI ejecuta el laboratorio en la rama Freebuff y verifica backup, restore y seis casos reales de Odoo. Los resultados observados y los commits se registran al finalizar.
