# Handoff · agntia-gestoria · 2026-11-14

Repositorio: `uniscrolliabrain-cloud/agntia-gestoria`. Base: `main` en `5dd9395`.
Entrega: rama `agent/gst-c09-ssrf-hardening`, commit `406f6ed`, PR #19.
Ámbito: GST-C09 y auditoría de estado. No se ha tocado el padre `agente`.

## Qué se entrega

| Elemento | Dónde |
|---|---|
| Rechazo de hosts numéricos ambiguos | `agntia_gestoria/integrations/registry.py` |
| Credencial acotada a ASCII imprimible 16–512 | `agntia_gestoria/integrations/registry.py` |
| Pruebas negativas y positivas | `tests/test_odoo_hardening.py::RegistryHardeningTests` |
| Auditoría de las 24 campañas | `docs/implementation/AUDIT-2026-11-14.md` |
| Estado ejecutado de la campaña | `docs/implementation/09-odoo-json-2-ssrf-acl/README.md` |

## Evidencia reproducible

```sh
python scripts/verify_baseline.py          # PASS · 43 ficheros · 45 rutas
python -m pytest -q                        # 189 passed · 6 skipped · 10 subtests
python -m unittest discover -s tests       # 94 tests OK (la suite del CI)
node typescript/scripts/build.mjs          # build OK · dist sin cambios
node --test typescript/tests/*.mjs         # 4/4 pass
```

Los 6 omitidos son la suite live de Odoo: exige laboratorio arrancado y
`AGNTIA_LAB_STATE_DIR`. No se han ejecutado Docker, Odoo, PostgreSQL ni restauración.

## Variables para Doppler

Nombres reales leídos por el código. Ningún valor debe viajar en el repositorio ni en un chat.

| Variable | Tipo | Ámbito | Notas |
|---|---|---|---|
| `GESTORIA_OWNER_TOKEN` | secreto | servicio | Token de propietario; rotar antes de exponer |
| `GESTORIA_ACTORS_JSON` | secreto | servicio | Mapa token → `{id, role, companies}`; contiene tokens |
| `GESTORIA_DATA_DIR` | plano | servicio | Ruta de datos; privada y fuera del checkout |
| `GESTORIA_PUBLIC_ORIGIN` | plano | servicio | Origen público para enlaces y CORS |
| `GESTORIA_MAX_UPLOAD_MB` | plano | servicio | Límite de subida |
| `GESTORIA_RRHH_JSON` | secreto | servicio | Empresas con RRHH activo; sin esta bandera la API responde 404 |
| `GESTORIA_RRHH_SECTOR` | plano | servicio | Sector del pack por defecto |
| `GESTORIA_RRHH_PACKS` | plano | servicio | Ruta de packs |
| `GESTORIA_SECURITY_CHAT_WEBHOOK` | secreto | servicio | Webhook de avisos; vacío deja avisos en memoria |
| `ODOO_ADAPTER_ENABLED` | plano | servicio | Interruptor maestro; por defecto apagado |
| `ODOO_IDENTITY_MODE` | plano | servicio | `standalone` en este repositorio |
| `ODOO_TEST_MODE` | plano | laboratorio | Habilita HTTP solo en pruebas |
| `ODOO_ALLOW_LOCAL_OWNER` | plano | desarrollo | Nunca en producción |
| `ODOO_SERVERS_JSON` | secreto | servicio | Definiciones de servidor, redes permitidas y nombres de las claves |
| `ODOO_BOT_KEY` (o el nombre que declare `api_key_env`) | secreto | servicio | Debe cumplir `[!-~]{16,512}`; rotación con revisión de binding |
| `ODOO_BRIDGE_SIGNING_KEY` (o el declarado) | secreto | servicio | Firma de aprobaciones |
| `ODOO_DOCUMENT_KEY` (vía `ODOO_DOCUMENT_KEY_ENV`) | secreto | servicio | Clave Fernet de documentos cifrados |
| `ODOO_DOCUMENT_KEY_ENV` | plano | servicio | Nombre de la variable que contiene la clave |
| `ODOO_REQUIRE_SCANNER` | plano | servicio | Exigir scanner antes de aceptar adjuntos |
| `ODOO_SCANNER_COMMAND_JSON` | secreto | servicio | Comando del scanner; no es un secreto pero revela rutas |
| `ODOO_ACTOR_SCOPES_JSON` | secreto | servicio | Alcance por actor |
| `PORT`, `HOST` | plano | servicio | Escucha del servicio |

Entornos: un juego por entorno (`dev`, `staging`, `prod`) en el proyecto Doppler del
repositorio. Los secretos de Odoo se rotan junto con la revisión de conexión: al cambiar la
clave hay que revalidar el binding, porque una credencial nueva sin revalidación deja el
alcance anterior en vigor. No se ha conectado ningún proveedor ni escrito valor alguno.

## Integración con el padre `agente`

Lo que este repositorio puede ofrecer hoy, sin cambios en el padre:

- Servicio HTTP con expedientes, informes, motores 303/130 y adaptador Odoo.
- SDK TypeScript con cliente y contrato de errores estable (`integrations/errors.py`, 60+ códigos).
- Catálogo de herramientas del agente limitado por capacidad y alcance de empresa.
- Cierre de expedientes reservado a roles humanos (`owner`, `reviewer`); el agente recibe 403.

Propuesta, no ejecutada:

1. Contrato de identidad. Este repositorio resuelve actores por token local. Para producción
   hace falta JWT del padre con `sub`, tenant y membresía; mientras no exista, la integración
   no puede considerarse autenticada de extremo a extremo (GST-C17 sigue `PENDING`).
2. Mandato y twins. Sin contrato acordado no se implementa nada localmente (GST-C18 `PENDING`).
3. Catálogo de lectura primero. Empezar por `res.partner` y facturas en lectura con flag por
   tenant apagado; las escrituras siguen bloqueadas hasta tener reconciliación con Odoo real.
4. Ningún cambio de contrato compartido se hace desde aquí: se propone y decide el fundador.

## Rollback

Revertir `406f6ed`. Los cambios son de validación, sin migración ni dato persistido: al
revertir, un binding con host ambiguo o credencial sucia volvería a aceptarse, y la política
de red seguiría siendo la única contención. No hay estado que conciliar.

## Pendiente y bloqueado

- Docker y Odoo real: GST-C02, C10, C11 y la verificación externa de C05–C09.
- Identidad del padre: GST-C17 y C18 requieren decisión, no código.
- Fiscalidad: GST-C14 y C15 no avanzan sin validación experta y fuentes.
- Cobertura medida en CI (GST-C12) y auditoría de licencias (GST-C16): trabajo acotado y sin
  dependencias externas, es el siguiente candidato natural.

## Para la auditoría independiente

Cada fila de `docs/implementation/AUDIT-2026-11-14.md` se puede reproducir con los comandos
del baseline. Donde dice `CODE_PRESENT` hay código y tests unitarios, no prueba en proveedor
real; donde dice `BLOCKED` falta entorno o decisión humana, no esfuerzo.
