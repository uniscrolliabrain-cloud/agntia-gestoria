/**
 * Conector de solo lectura entre el runtime de Agente y el middleware Gestoría.
 *
 * No contiene herramientas que aprueben, exporten ni escriban en Odoo: esas
 * operaciones son humanas y se quedan en la UI. El token viaja solo en servidor.
 */

export type GestoriaOptions = {
  baseUrl: string;
  token: string;
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
};

export type GestoriaErrorBody = { code?: string; message?: string };

export class GestoriaError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "GestoriaError";
  }
}

type Json = Record<string, unknown>;

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
      const body = (text ? JSON.parse(text) : {}) as Json;
      if (!response.ok) {
        const detail = (body.detail ?? {}) as GestoriaErrorBody;
        throw new GestoriaError(
          response.status,
          String(detail.code ?? "http_error"),
          String(detail.message ?? response.statusText),
        );
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
export const readOnlyTools = (client: GestoriaClient): ToolDescriptor[] => [
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
  {
    name: "rrhh.closure.prepare",
    description: "Prepara el cierre del periodo (idempotente, sin escribir en Odoo).",
    mutates: true,
  },
];

/** Operaciones que solo ejecuta una persona desde la UI. */
export const humanOnly = ["rrhh.closure.approve", "rrhh.closure.export"] as const;

export function isHumanOnly(name: string): boolean {
  return (humanOnly as readonly string[]).includes(name);
}

export type { GestoriaClient as Client };
