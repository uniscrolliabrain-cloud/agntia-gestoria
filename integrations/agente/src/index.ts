/**
 * Conector entre el runtime de Agente y el middleware Gestoría.
 *
 * Catálogos separados (C04): `readOnlyTools` no contiene ninguna herramienta que
 * mute estado; las propuestas viven en `proposalTools`. Las operaciones que solo
 * ejecuta una persona se enumeran en `humanOnly` y nunca se ofrecen al agente.
 *
 * Contratos de error (C05): el servicio emite `{code,message}` en las rutas de
 * integración y `{detail:...}` en las genéricas. `parseFailure` acepta ambas
 * formas y las de validación de FastAPI, sin devolver el cuerpo crudo.
 */

export type GestoriaOptions = {
  baseUrl: string;
  token: string;
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
};

export type GestoriaErrorBody = { code?: string; message?: string };

export class GestoriaError extends Error {
  // Campos explícitos, no propiedades de parámetro: así el módulo se puede
  // ejecutar directamente con el runner de Node sin compilar.
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
    this.name = "GestoriaError";
  }
}

type Json = Record<string, unknown>;

export const defaultStatusCode = (status: number): string => {
  if (status === 401) return "auth";
  if (status === 403) return "forbidden";
  if (status === 404) return "not_found";
  if (status === 409) return "conflict";
  if (status === 422) return "validation";
  if (status === 424) return "not_configured";
  if (status === 429) return "rate_limit";
  if (status === 503) return "provider_unavailable";
  return "http_error";
};

const asRecord = (value: unknown): Json | null =>
  value !== null && typeof value === "object" && !Array.isArray(value) ? (value as unknown as Json) : null;

/** Extrae un código y un mensaje estables de cualquiera de las formas emitidas. */
export function parseFailure(
  status: number,
  body: unknown,
  statusText = "",
): { code: string; message: string } {
  const fallbackCode = defaultStatusCode(status);
  const top = asRecord(body);
  if (!top) return { code: fallbackCode, message: statusText || `HTTP ${status}` };
  const directCode = top.code;
  const directMessage = top.message;
  if (typeof directCode === "string" && directCode) {
    return {
      code: directCode,
      message: typeof directMessage === "string" && directMessage ? directMessage : statusText || `HTTP ${status}`,
    };
  }
  const detail = top.detail;
  const nested = asRecord(detail);
  if (nested && typeof nested.code === "string" && nested.code) {
    const nestedMessage = nested.message;
    return {
      code: nested.code,
      message: typeof nestedMessage === "string" && nestedMessage ? nestedMessage : statusText || `HTTP ${status}`,
    };
  }
  if (typeof detail === "string" && detail) return { code: fallbackCode, message: detail };
  if (Array.isArray(detail)) {
    const first = asRecord(detail[0]);
    const message = first && typeof first.msg === "string" ? first.msg : "Entrada inválida";
    return { code: "validation", message };
  }
  return { code: fallbackCode, message: statusText || `HTTP ${status}` };
}

export function createGestoriaClient(options: GestoriaOptions) {
  const base = options.baseUrl.replace(/\/+$/, "");
  const doFetch = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? 15_000;

  async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await doFetch(`${base}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${options.token}`,
          ...(init.headers ?? {}),
        },
        signal: controller.signal,
      });
      const text = await response.text();
      let body: unknown = {};
      if (text) {
        try {
          body = JSON.parse(text) as unknown;
        } catch {
          // Nunca se propaga el cuerpo crudo: puede contener HTML o trazas.
          body = { detail: undefined, unparsable: true };
        }
      }
      if (!response.ok) {
        const failure = parseFailure(response.status, body, response.statusText);
        throw new GestoriaError(response.status, failure.code, failure.message);
      }
      return body as T;
    } finally {
      clearTimeout(timer);
    }
  }

  return {
    capabilities: (companyId: string) =>
      call<Json>(`/api/companies/${companyId}/rrhh/capabilities`),
    health: (companyId: string) => call<Json>(`/api/companies/${companyId}/rrhh/health`),
    policy: (companyId: string) => call<Json>(`/api/companies/${companyId}/rrhh/policy`),
    closure: (companyId: string, period: string) =>
      call<Json>(`/api/companies/${companyId}/rrhh/closures/${period}`),
    audit: (companyId: string) => call<Json>(`/api/companies/${companyId}/rrhh/audit`),
    securityDigest: () => call<Json>("/api/security/digest"),
  };
}

export type GestoriaClient = ReturnType<typeof createGestoriaClient>;

export type ToolDescriptor = {
  name: string;
  description: string;
  mutates: boolean;
};

/** Lo que un agente puede consumir sin privilegios de escritura. */
export const readOnlyTools = (_client: GestoriaClient): ToolDescriptor[] => [
  {
    name: "rrhh.capabilities",
    description: "Comprueba si RR. HH. está encendido para la empresa.",
    mutates: false,
  },
  {
    name: "rrhh.health",
    description: "Estado del módulo, último snapshot y proveedor de nómina.",
    mutates: false,
  },
  {
    name: "rrhh.closure.read",
    description: "Lee el último cierre del periodo con sus incidencias.",
    mutates: false,
  },
  {
    name: "rrhh.audit.read",
    description: "Lee la cadena de auditoría y si está íntegra.",
    mutates: false,
  },
  {
    name: "security.digest",
    description: "Resumen de lo observado por el agente de seguridad.",
    mutates: false,
  },
];

/**
 * Propuestas: preparan trabajo pero no lo confirman. Un agente puede
 * invocarlas; el efecto sensible sigue exigiendo aprobación humana.
 */
export const proposalTools = (_client: GestoriaClient): ToolDescriptor[] => [
  {
    name: "rrhh.closure.prepare",
    description: "Prepara el cierre del periodo (idempotente, sin escribir en Odoo).",
    mutates: true,
  },
];

/** Catálogo completo del conector, con lectura y propuestas separadas por origen. */
export const gestoriaTools = (client: GestoriaClient): ToolDescriptor[] => [
  ...readOnlyTools(client),
  ...proposalTools(client),
];

/** Operaciones que solo ejecuta una persona desde la UI. */
export const humanOnly = ["rrhh.closure.approve", "rrhh.closure.export"] as const;

export function isHumanOnly(name: string): boolean {
  return (humanOnly as readonly string[]).includes(name);
}

export type { GestoriaClient as Client };
