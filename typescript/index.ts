export class GestoriaError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) { super(typeof detail === 'string' ? detail : JSON.stringify(detail)); this.status = status; this.detail = detail; }
}
/** Keep tokens on the server. The backend enforces actor roles and company scope. */
export class Gestoria {
  private baseUrl: string;
  private token: string;
  constructor(baseUrl: string, token: string) {
    this.baseUrl = baseUrl; this.token = token;
    const url = new URL(baseUrl);
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Invalid service URL');
  }
  async request<T = unknown>(path: string, body?: unknown, method = body === undefined ? 'GET' : 'POST'): Promise<T> {
    if (!path.startsWith('/api/') || path.includes('..') || path.includes('\\') || path.includes('#')) throw new Error('Invalid API path');
    const response = await fetch(new URL(path, this.baseUrl), {
      method, redirect: 'error', headers: { Authorization: `Bearer ${this.token}`, ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}) },
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(30000),
    });
    const result = await response.json();
    if (!response.ok) throw new GestoriaError(response.status, result.detail ?? result);
    return result as T;
  }
  companies() { return this.request('/api/companies'); }
  obligations(companyId: string) { return this.request(`/api/companies/${id(companyId)}/obligations`); }
  dashboard(companyId: string, year: number) { if (!Number.isInteger(year) || year < 2000 || year > 2100) throw new Error('Invalid year'); return this.request(`/api/companies/${id(companyId)}/dashboard?year=${year}`); }
  calculate(companyId: string, input: Record<string, unknown>) { return this.request(`/api/companies/${id(companyId)}/tax-calculations`, input); }
  createReport(companyId: string, year: number) { return this.request(`/api/companies/${id(companyId)}/reports`, { year }); }
  cases(companyId: string) { return this.request(`/api/companies/${id(companyId)}/cases`); }
  createCase(companyId: string, draft: Record<string, unknown>) { return this.request(`/api/companies/${id(companyId)}/cases`, draft); }
  propose(companyId: string, revision: number) { return this.request(`/api/companies/${id(companyId)}/generate-plan`, { revision }); }
}
export function id(value: string) { if (!/^[a-f0-9]{32}$/.test(value)) throw new Error('Invalid identifier'); return value; }
