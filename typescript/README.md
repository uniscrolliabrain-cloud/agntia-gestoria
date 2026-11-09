# @agntia/gestoria

Cliente TypeScript para Node >=22.13; incluye JavaScript compilado y declaraciones de tipos, el adaptador Hono requiere Hono en la aplicación anfitriona. Instala este directorio con pnpm. No contiene el servicio Python: instálalo y arráncalo por separado.

Monta `gestoriaRoutes` en `/api`, con una función `forActor` que autentique al usuario de Hono y seleccione sus credenciales de servicio. No expongas un token owner común. Los uploads y descargas se realizan con las rutas del servicio, autorizados en el servidor.

`agentTools(client, companyId)` devuelve herramientas independientes del proveedor de LLM. No incluye una herramienta de aprobación humana. Usa siempre tokens agent y valida las entradas mediante el esquema de herramientas de tu framework antes de ejecutarlas. El backend vuelve a validar cada petición.

Incluye herramientas de cálculo 303/130 acotado y dashboard/informes. Las herramientas de agentes no exponen la revisión de registros. El anfitrión selecciona modelos y valida parámetros con su framework; no se incluye una conexión automática a proveedores de LLM.
