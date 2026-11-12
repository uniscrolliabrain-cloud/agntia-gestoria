# Agente de ciberseguridad (solo lectura)

Un observador que ve pasar todo lo que ocurre en el servicio y lo cuenta por
chat. No maneja el runtime del agente: no bloquea, no ejecuta, no cambia
políticas y no puede leer credenciales. Si alguna vez se le añade poder, la
prueba `test_the_agent_only_reads_and_says_so` falla a propósito.

## Qué ve

`SecurityMiddleware` envuelve la aplicación y anota cada petición terminada:

- método, ruta (recortada a 300 caracteres), estado HTTP y duración en ms;
- actor autenticado cuando la ruta lo resuelve, y empresa;
- un motivo y una gravedad deducidos de la propia petición.

Nunca guarda cuerpos, cabeceras de credencial ni `Authorization`: `redact()`
sustituye cualquier cabecera sensible por `<redactado>` antes de que exista
cualquier registro.

## Cómo clasifica

| Motivo | Gravedad | Cuándo |
|---|---|---|
| `path_traversal` | crítica | ruta con secuencias de subida de directorio o byte nulo |
| `server_error` | alta | estado 500 o superior, o excepción no controlada |
| `auth_denied` | aviso | 401 y 403 |
| `rate_limited` | aviso | 429 |
| `client_error` | info | 400–499 restantes |
| `rrhh_write` | info | escritura sobre `/rrhh/` (cierre, aprobación) |
| `ok` | info | el resto |

La ventana en memoria es de 500 eventos y se reinicia con el proceso. Es
deliberado: el rastro permanente y encadenado es el de `rrhh/audit`, no este.

## Patrones

Además de contar, `anomalies()` agrupa lo que suele pasar desapercibido:

| Patrón | Umbral | Qué dice |
|---|---|---|
| `auth_burst` | 3 denegaciones del mismo actor | posible fuerza bruta o credencial caducada |
| `server_errors` | 2 fallos 500 en la ventana | el servicio está fallando, no el cliente |
| `critical_path` | 1 evento crítico | ruta con travesía u otro intento evidente |

Una sola denegación no es un patrón: se evita convertir ruido normal en alarma.

## Cómo habla

`GET /api/security/digest` devuelve el resumen sin enviarlo. `POST
/api/security/report` lo envía al canal configurado y devuelve lo mismo que
muestra el chat:

```
Seguridad · 12 peticiones observadas.
Por gravedad: info 9, warning 2, high 1, critical 0.
1 alertas que requieren mirada humana:
 · 2026-11-12T09:14:03+00:00 GET /api/companies/…/rrhh/closures → 500 (812 ms). …
Patrones:
 · 3 accesos denegados para el mismo actor.
Solo lectura: no he modificado ni bloqueado nada.
```

`GESTORIA_SECURITY_CHAT_WEBHOOK` apunta a Slack, Teams, Matrix o el webhook del
propio runtime; si está vacío, los mensajes se guardan en memoria para
inspección local. El `Notifier` limita a un aviso por minuto para no inundar el
chat, y un webhook caído devuelve `delivered: false` sin tumbar el servicio.
`GET /api/security/chat` devuelve el historial de lo enviado cuando el canal es
local.

## Rastro de auditoría por CLI

El agente no puede arreglar una cadena rota, pero sí señalarla sin arrancar el
servicio:

```bash
python -m agntia_gestoria.integrations.security --db .agente --company <hex32>
```

Devuelve `0` si la cadena es válida, `1` si está rota (con el número de secuencia)
y `2` si el identificador no es válido. Solo lee.

## Permisos

`/api/security/*` exige rol `owner`. Un `reviewer` o un `viewer` recibe 403.
`/watchlist` publica explícitamente lo que el agente **no** puede hacer, para que
nadie le suponga más poder del que tiene.

## Pruebas

```bash
.venv/bin/python -m pytest -q tests/test_security_watcher.py \
    tests/test_security_agent_api.py tests/test_security_anomalies.py
```

Cubren redacción, clasificación, ventana acotada, middleware con éxito y con
excepción, contrato de solo lectura, patrones, resumen sin credenciales, límite
de avisos, permisos de las rutas y la CLI.

## Lo que falta para vigilar de verdad

- Enviar los avisos al bus de eventos del runtime padre en lugar de sólo un
  webhook (necesita el contrato de eventos de `agente`).
- Correlacionar por `correlationId` con las operaciones de Odoo.
- Alertar de credenciales caducadas: hoy se ve el 401, no su causa.
