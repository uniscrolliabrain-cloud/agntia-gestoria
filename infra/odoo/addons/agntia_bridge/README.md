# agntia_bridge

Código propio LGPL-3, versión19.0.1.0.0. Dependencias: base, contacts y rpc. Instalar solo en laboratorio Odoo Community19 fijado al SHA de infra/odoo/Dockerfile antes de piloto. No ejecutado/instalado en el entorno implementador.

El grupo agntia_bridge.group_integration es exclusivo de la cuenta bot restringida: no añadir base.group_system, account.group_account_invoice ni otros grupos de escritura. Comprobar grupos efectivos/ACL después de cada módulo. El bridge rechaza superusuario y limita compañía/context; las escrituras exigen un marcador Python interno y aprobación HMAC del servidor Gestoría. Montar el verificador en /run/secrets/agntia_bridge_signing_key, nunca en parámetros de un agente.

No publicar, enviar, pagar, presentar ni borrar movimientos. Ningún método genérico de ejecución de modelos está expuesto por este addon. Usar el ledger y operation_status para reconciliar replays/timeout. Las ACL/guardas, transacciones y concurrencia deben validarse con PostgreSQL real: leer docs/odoo-adapter/pilot-acceptance.md. No conceder permisos admin para hacer pasar una prueba.

Para instalar/testear ver scripts/odoo_verify.ps1 y docs/odoo-adapter/RUNBOOK.md desde la raíz del repositorio. No es un addon de cumplimiento fiscal universal ni reemplaza la localización española o revisión competente.
