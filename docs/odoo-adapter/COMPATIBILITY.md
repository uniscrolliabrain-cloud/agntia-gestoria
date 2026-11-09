# Compatibilidad y licencia

Objetivo estricto: Community autogestionado 19.0, core `60657b50d171ddf84ab58717fdee5ac26031065b`. Dockerfile sobre base digest auditado y fuente exacta superpuesta. PostgreSQL17-bookworm por digest documentado en infra/odoo; no se ha descargado o arrancado aquí. Build/instalación/ACL reales NOT VERIFIED.

El bridge/base permite diagnóstico/contactos sin account; la extensión bridge_account depende de account. l10n_es se instala solo en el laboratorio; su existencia no certifica cobertura de todas las obligaciones españolas. Ningún módulo OCA se copia o instala por defecto. Enterprise se rechaza en discovery; no se promete Odoo Online. Versiones16/17/18/20 no soportadas por este mapping.

Python >=3.11, implementación comprobada localmente con3.12. SDK Node >=22.13, build usa stripTypeScriptTypes. Cliente/exports anteriores conservados. Hono peer opcional ^4.10. Versiones exactas del entorno de pruebas están en c20/local-results.json. APIs nuevas solo backend; no credenciales en navegador.

El código propio del paquete conserva su licencia existente; addons propios LGPL-3 por manifiesto. Core Odoo LGPLv3, addons con términos particulares. Preferimos API y checkout de fuente en imagen en vez de copiar archivos al repo. Distribuir la imagen exige conservar avisos y acceso al código/modificaciones conforme a las licencias aplicables; revisar dependencias de sistema y cualquier OCA AGPL antes de distribución comercial. Ver auditoría previa odoo19-licensing.md. Esto es una lista técnica de obligaciones a revisar, no asesoramiento jurídico universal.
