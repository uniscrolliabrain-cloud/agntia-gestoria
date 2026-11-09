# Agntia-gestoria

Asistente de gestión para autónomos y SL españolas, con interfaz web, API para agentes y cliente TypeScript. Incluye dashboard con gráficos mensuales y alertas explicables, reportes PDF/PowerPoint/HTML e infografías SVG, motores acotados 303 y 130 para 2026, registro económico con documentos y referencias únicas, expedientes de preparación fiscal con detección de datos modificados, perfiles de empresas, propuestas de obligaciones con fuentes, expedientes con revisión humana, documentos, borradores económicos, agenda y trazabilidad.

## Instalar

Python 3.11 o superior, en Windows o Linux:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
pip install .
agntia-gestoria
```

Abre http://127.0.0.1:8010. Sin credenciales solo permite acceso local. Para un servidor, configura `GESTORIA_OWNER_TOKEN` con un secreto aleatorio de al menos 16 caracteres antes de arrancar, usa HTTPS y limita el acceso de red. `GESTORIA_DATA_DIR` contiene SQLite y documentos: inclúyelo en copias de seguridad protegidas. No lo subas a GitHub.

También puedes configurar `GESTORIA_ACTORS_JSON`: objeto cuyas claves son tokens y cuyos valores son `{ "id": "agente-1", "role": "agent", "companies": ["ID_EMPRESA"] }`. Roles: owner, reviewer, agent, viewer. Solo owner crea empresas. Solo owner/reviewer aprueba expedientes. Tokens siempre en el servidor, nunca en el frontend público. Los documentos son contenido no confiable; los agentes no deben interpretar instrucciones dentro de ellos como permisos.

## TypeScript, Hono y pnpm

Python se instala con pip y funciona como servicio independiente; pnpm instala el cliente del directorio `typescript`:

```sh
pnpm add ./ruta/Agntia-gestoria/typescript
```

```ts
import { Gestoria } from '@agntia/gestoria';
const gestoria = new Gestoria('http://127.0.0.1:8010', process.env.GESTORIA_TOKEN!);
const companies = await gestoria.request('/api/companies');
```

El cliente exporta un adaptador Hono y herramientas para agentes. La aplicación anfitriona debe autenticar y autorizar a cada usuario antes de invocar el adaptador. Asigna a los agentes tokens de rol agent, limitados a sus empresas. No compartas con ellos el token owner.

## Alcance actual

El perfil permite declarar actividad en varios territorios: territorio común, Canarias, Álava/Araba, Bizkaia, Gipuzkoa, Navarra, Ceuta y Melilla, con administraciones declaradas por impuesto. Se generan expedientes de preparación territorial con sus fuentes. El cálculo fiscal territorial completo, los puntos de conexión y los repartos todavía requieren revisión específica; las reglas automáticas de territorio común no se extrapolan a perfiles mixtos o especiales. Los hechos desconocidos generan preguntas, no exenciones automáticas. Las fechas calculadas son nominales y requieren contrastar el calendario oficial, festivos y domiciliación. Los motores 303 y 130 calculan los supuestos admitidos para territorio común, con documentos, revisión de registros y fórmulas trazables. Consulta [ámbito y exclusiones](docs/calculation-engines.md). La revisión es interna: no presenta declaraciones, no emite facturas fiscales ni certifica cumplimiento SIF/VERI*FACTU. Los borradores contables comprueban equilibrio, no adecuación del asiento al PGC.

Fuentes revisadas el 9 de noviembre de 2026, con siguiente revisión prevista el 9 de diciembre. Consulta [investigación legal](docs/legal-research.md) y [repositorios estudiados](docs/repositories.md). No se ha copiado código de estos proyectos.

## Desarrollo

```sh
pip install -e '.[dev]'
python -m unittest discover -s tests -v
```

MIT. Proyecto inicial, sin conectores de presentación ante administraciones ni automatización bancaria. El dashboard y las exportaciones se explican en [datos e informes](docs/dashboard-and-reports.md).

El [alcance de gestoría completa](docs/product-scope.md) recoge renta anual, IVA, pagos de IRPF, retenciones, sociedades, laboral, representación y conservación de datos, y distingue lo implementado de los motores y conectores pendientes para regímenes y modelos aún no admitidos. Registrar un modelo en un expediente no equivale a tener su liquidación implementada.
