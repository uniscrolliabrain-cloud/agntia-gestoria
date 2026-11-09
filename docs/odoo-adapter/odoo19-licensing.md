# Licencias · C02

El LICENSE del commit Odoo fijado declara LGPLv3, incluye el texto GPL al que añade permisos y advierte que componentes externos pueden tener otras licencias compatibles. Los manifiestos inspeccionados de base, account, contacts, rpc y l10n_es declaran `LGPL-3`.

El adaptador se diseñará como cliente de API independiente, sin copiar código upstream dentro del paquete MIT de Agntia Gestoría. Las fuentes se han leído en una carpeta de referencia externa al repositorio; en esta entrega solo se añaden hashes, referencias y comprobaciones propias del contrato. No se distribuye un addon derivado de Odoo ni Enterprise.

OCA/l10n-spain no se instala. Cada addon futuro requiere revisar licencia de su versión exacta, dependencias y obligaciones de distribución/uso en red; no se presume que todos los módulos sean AGPL ni que la licencia MIT propia los relicencie. No se ha realizado una evaluación exhaustiva de las dependencias de la imagen oficial.

Referencias fijadas en `infra/odoo/upstream-lock.json`: LICENSE, manifiestos y receta de imagen. Una integración por API no exime de cumplir las licencias de los componentes que posteriormente se distribuyan o modifiquen. La decisión sobre el eventual agntia_bridge sigue pendiente de C16/C17.
