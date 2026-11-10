# C06 · Registro de conexiones y resolución de credenciales

Estado: primer corte aislado sobre las migraciones de la PR #9. Incluye configuración de servidor, registro pendiente, proyección pública, rotación, desactivación y resolución interna de lectura.

El servidor compone el catálogo con referencias de endpoint, DB y clave. El operador fija los hosts permitidos. Un principal se construye después de autenticar y comprobar pertenencia a tenant y empresa. La relación entre tenant y empresa debe existir previamente en el almacén. El registro comprueba este scope y el rol de propietario antes de consultar la configuración. Ningún método de este módulo acepta una URL procedente de la solicitud de un agente.

| Cambio | Regla |
| --- | --- |
| Registrar | Propietario del scope. Solo referencias existentes. Estado inicial `pending_validation`. |
| Rotar | Propietario y revisión exacta. Cambia la referencia e invalida el estado activo. |
| Desactivar | Propietario y revisión exacta. Las resoluciones siguientes se deniegan. |
| Resolver lectura | Scope exacto y estado activo antes de consultar el proveedor de secretos. Los resultados públicos omiten las referencias internas. |

La validación del origen es sintáctica y exige un hostname exacto autorizado y HTTPS. HTTP se limita a loopback literal cuando el operador activa expresamente el modo de prueba. La resolución DNS y el control de la conexión efectiva corresponden a C07. El ejecutor debe comprobar de nuevo el scope y la revisión al preparar cada operación; un cambio posterior a una petición en curso se trata como un estado concurrente.

La activación tras discovery, el aprovisionamiento de pertenencia, el transporte y los endpoints de administración quedan pendientes. Las pruebas usan un proveedor sintético de secretos y activación controlada de fixtures. No hay tráfico externo.

## Pruebas

`python -m unittest discover -s tests -p test_odoo_registry.py -v`

Casos de roles, tenant ajeno, referencias duplicadas, estado pendiente, rotación y revisión obsoleta, desactivación, URL ambigua, filtración en salidas públicas y sanitización de fallos del proveedor.
