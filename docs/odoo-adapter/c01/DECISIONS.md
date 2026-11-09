# Decisiones y changelog C01

## ADR-C01-001 · Referencia remota más igualdad del árbol

Se usa el SHA remoto como baseline público y el árbol Git como prueba de igualdad del checkout. Se registra el SHA local diferente en lugar de afirmar un checkout remoto inexistente. Un intento de reconstrucción canónica de objetos commit remotos no reprodujo sus hashes; no se movió ninguna ref a esos objetos. La rama remota se creó mediante GitHub desde el SHA comprobado.

## ADR-C01-002 · Verificación sin importar la aplicación

El script usa AST, texto y SHA-256. No llama a `create_app`, no abre SQLite ni lee configuración de actores. El inventario de roles recoge argumentos explícitos de `require_role`; no constituye por sí solo una prueba de autorización o aislamiento.

## ADR-C01-003 · No reparar producción para hacer pasar el baseline

Se conservan las dependencias, código y pruebas actuales. Los fallos offline/sockets se registran separados del resultado de CI. El ajuste temporal del selector solo permite ejecutar las 23 pruebas en el sandbox; no sustituye el comando estándar en GitHub.

## ADR-C01-004 · Secuencia y autorización

La campaña exige una PR por fase y revisión/fusión secuencial, y prohíbe presumir permiso para fusionar. C01 puede abrirse y verificarse; C02 no se declara iniciado ni aprobado antes del cierre de ese gate. No se implementan archivos de C04 en paralelo para saltarlo. No se solicita ni se utiliza ningún secreto de un cliente.
