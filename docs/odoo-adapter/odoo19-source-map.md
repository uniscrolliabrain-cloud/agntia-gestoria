# Mapa de fuentes Odoo 19.0 · C02

Referencia fijada: [odoo/odoo@60657b50d171ddf84ab58717fdee5ac26031065b](https://github.com/odoo/odoo/tree/60657b50d171ddf84ab58717fdee5ac26031065b). Consulta: 09/11/2026. SHA-256, tamaño y URL exacta de cada fuente en `infra/odoo/upstream-lock.json`. Las copias inspeccionadas están fuera del repositorio del producto y no se redistribuyen como código propio.

| Fuente | Observación comprobada | Decisión para el futuro adaptador |
| --- | --- | --- |
| `addons/rpc/controllers/json2.py:49–90` | Handler POST, auth bearer, sin sesión; argumentos por nombre, ids/context, resolución de método público y retorno directo. | Lista cerrada de operaciones; no endpoint genérico model/method. No reenviar traceback remoto. |
| `addons/rpc/__manifest__.py` | Addon Community LGPL-3, depende de base y declara auto_install. | Comprobar instalación efectiva y permisos en discovery; el manifiesto no prueba disponibilidad del endpoint. |
| `addons/account/models/account_move.py:130–182` | Estados draft/posted/cancel y tipos de factura, abono y asiento; compañía, diario y line_ids. | Filtrar compañía, estado y move_type explícitamente; prohibir action_post/unlink y asientos en la proyección inicial. |
| `account_move.py:366–374` | invoice_line_ids es subconjunto de line_ids e incluye producto, sección, subsección y nota. | Ni siquiera invoice_line_ids puede sumarse sin filtrar display_type y reconciliar totales. |
| `account_move_line.py:333–351` | Líneas técnicas: tax, payment_term, rounding, descuentos y otras variantes no son ventas/gastos ordinarios. | Evitar doble cómputo; excepciones a mapping_blocked, no omisiones silenciosas. |
| `account_move_line.py:195–216,383–418` | tax_ids, tax_line_id, cantidades, descuento y subtotales/totales separados. | Conciliar por factura/moneda; no inferir que subtotal más porcentaje único reproduce todos los impuestos. |
| `account_tax.py:80–160` | Impuestos agrupados, fijos, porcentaje/división; compañía, impuestos incluidos y subimpuestos. | Un importe 21 no demuestra IVA ni deducibilidad; verificación fiscal separada. |
| `account_account.py:97–100` | La cuenta usa `company_ids` Many2many, no `company_id` singular. | Discovery y dominios específicos de Odoo 19; no reutilizar un filtro de versiones antiguas. |
| `odoo/addons/base/models/res_partner.py:213–285` | Campos fiscales/contacto y compañía, algunos con anotación de tipo. | Lectura mínima y binding por ID; nombre/NIF no equivalen a identidad del tenant. |
| `odoo/addons/base/security/base_security.xml:12–20` | La regla de partners permite registros globales e incluye excepción de usuarios internos. | No confiar exclusivamente en la record rule para aislamiento. Excluir por defecto globales/ajenos hasta política explícita y tests. |
| `addons/account/security/account_security.xml:128–179` | Reglas por compañía; algunas usan parent_of y cuentas usan company_ids. | Exigir pertenencia exacta del binding aunque la jerarquía Odoo conceda más acceso. |
| `addons/account/security/ir.model.access.csv:33–78` | Grupos readonly y billing tienen permisos diferentes; billing permite create/write/unlink en movimientos. | Un bot de escritura requiere policy adicional; pertenecer a billing no autoriza publicar ni eliminar. |
| `addons/l10n_es/__manifest__.py` | Depende de account/base_iban/base_vat/account_edi_ubl_cii; declara datos de modelos españoles, incluido mod420. | Se corrige la ruta `manifest.py` citada en la campaña: el archivo real es `__manifest__.py`. Plantillas presentes no prueban instalación, exactitud fiscal ni presentación. |
| `odoo/release.py` | Serie 19.0, mínimo Python 3.10 y mínimo PostgreSQL 13 declarados por upstream. | Elegir versión PostgreSQL del laboratorio mediante prueba real; no confundir mínimo de código con compatibilidad ensayada. |

## Documentación oficial

La página HTML oficial dio timeout en el primer intento. Se inspeccionó su fuente primaria [external_api.rst fijada](https://github.com/odoo/documentation/blob/67e8ded4a03d7c53be4e2c4d53471678e9e9352e/content/developer/reference/external_api.rst). Documenta `Authorization: bearer`, `X-Odoo-Database`, respuesta JSON directa, errores con información sensible y una transacción independiente por llamada. Recomienda agrupar operaciones que deban ser atómicas. `search_read` evita la carrera entre search y read separados.

La advertencia de planes comerciales alojados no demuestra que un despliegue Community autogestionado carezca de JSON-2: el código existe en Community. Tampoco prueba que esté operativo en una instalación concreta. Eso sigue NOT VERIFIED.

## Diferencia entre código fijado e imagen

El SHA de referencia del código y el paquete nightly de la imagen oficial no se equiparan. La imagen observada usa el paquete 19.0 de 02/11/2026; no se ha demostrado que contenga exactamente el commit del 09/11/2026 fijado arriba. Antes del gate de integración se debe documentar esa correspondencia o construir un laboratorio desde el SHA exacto. No se instala ni modifica upstream en C02.
