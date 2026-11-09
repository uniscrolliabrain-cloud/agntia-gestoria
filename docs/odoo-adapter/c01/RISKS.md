# Riesgos observados C01

| Riesgo | Evidencia | Tratamiento |
| --- | --- | --- |
| Volcado no disponible | No se ha encontrado `agntia-gestoria.txt` | Comparación con snapshot NOT VERIFIED; baseline remoto identificado. |
| Dev offline incompleto | pip no encuentra pytest con `--no-index` | No cambiar dependencias; ejecutar instalación dev normal en CI. |
| TestClient bloqueado localmente | Suite estándar: timeout 15 s | Log y workaround test-only; CI estándar requerido para gate. |
| Navegador local sin sockets | `browser_check.py`: PermissionError al bind | No afirmar E2E local; ejecutar el script original en CI. |
| Docker no accesible | daemon existente, UID 1000, socket devuelve permission denied | Laboratorio C03 NOT VERIFIED; no reiniciar daemon ni usar otro host Docker. |
| Tenancy futura | `Actor` actual solo incluye id/role/companies | No aceptar tenant, company Odoo o scopes escritos por LLM como autorización. Resolver C04–C09 antes de tráfico Odoo. |
| Proxy Hono genérico actual | Rutas por prefijo y métodos GET/POST/PUT | C18 debe excluir proxy libre para Odoo y aplicar allowlist nominada. |
| Auditoría actual | Hashes por empresa; no verificador expuesto | No confundir con inmutabilidad legal. Extensión aditiva prevista por la campaña. |
| Suposiciones contables | TaxRecord y borradores no son facturas emitidas | Ninguna importación futura se marcará reviewed automáticamente; sin action_post. |

La inspección y las 23 pruebas existentes no son una auditoría exhaustiva ni verifican integración Odoo. No hay prueba de filtración, publicación fiscal o error de cálculo en esta fase. Si aparece una stop condition de la campaña, detener la fase afectada y documentarla.
