# C01 · Baseline antes del adaptador Odoo

Fecha: 2026-11-09. Repositorio: `uniscrolliabrain-cloud/agntia-gestoria`.

## Referencia congelada

- `main` remoto observado: `ae8db06bf548fa7c190a2ee5e5acf52075e343ba`.
- Árbol Git remoto y local: `572b06b1ea2bec2307d94136eb742bc5dcb61081`.
- Commit local previo: `bcb3dda`. Su historial difiere del remoto porque las publicaciones anteriores se hicieron mediante la API Git de GitHub. La igualdad del árbol demuestra identidad de archivos, modos y rutas; no identidad de los commits.
- Historial remoto consultado: `ae8db06` (corrección móvil), `49ba972` (implementación del servicio) y `55babb8` (README inicial).
- La rama remota `feat/odoo-c01-baseline` parte exactamente de `ae8db06`. El trabajo local usa la copia cuyo árbol se ha verificado idéntico. No se reescribe el historial de `main`.
- 43 archivos originales; 210.759 bytes y 2.625 líneas, contando todos los archivos versionados, incluidos los JavaScript compilados. Inventario SHA-256, firmas y 43 rutas API en [baseline-inventory.json](c01/baseline-inventory.json). El montaje de estáticos no se cuenta como endpoint de negocio.

## Comparación con el volcado citado por la campaña

El archivo `agntia-gestoria.txt` no está adjunto ni disponible en el workspace. La descripción del propietario indica 2.813 líneas y aproximadamente 205 KB; sus separadores y formato de volcado no son comparables directamente con el recuento de archivos. La comparación byte a byte con ese documento queda **NOT VERIFIED**. No se afirma haber leído un adjunto ausente. La fuente comprobada de implementación es `main`, con SHA y árbol anteriores.

## Arquitectura observada

FastAPI `create_app`, SQLite WAL con companies/objects/audit, documentos locales, frontend estático y paquete TS/Hono. No existen adaptador, conexión Odoo, bindings tenant/DB, tablas de sincronización ni un servicio de aprobaciones de AgntiaPro. No hay credenciales Odoo configuradas ni acceso a datos reales en esta campaña.

Se preservan: fórmulas 303/130 y su ámbito, reglas territoriales, validación de revisiones, separación de roles, estados internos de expedientes y borradores, documentos y hash de auditoría. Los resultados fiscales no acreditan una presentación. Ningún trabajo de C01 cambia esos archivos.

## Resultado y límites

Los resultados locales están en [TESTS](c01/TESTS.md) y sus logs. Instalación runtime, 23 tests con workaround de selector del sandbox, build Node, sintaxis y verificación de archivos: PASS. La suite estándar sin workaround se bloquea localmente; la instalación dev offline carece de pytest; navegador y Docker encuentran restricciones de sockets. No se contabilizan esos intentos como pruebas aprobadas. La suite estándar (23/23) y el navegador se ejecutaron de nuevo en CI sobre la rama C01 y aprobaron; su resultado se referencia en [EVIDENCE](c01/EVIDENCE.md).

Esta fase entrega reproducibilidad y evidencias, no un adaptador implementado. Las siguientes fases siguen condicionadas a sus gates y a la revisión/fusión secuencial autorizada por el propietario. No se modifica `agente`, upstream Odoo, producción ni secretos.
