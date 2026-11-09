export class GestoriaError extends Error {
  status        ;
  detail         ;
  constructor(status        , detail         ) { super(typeof detail === 'string' ? detail : JSON.stringify(detail)); this.status = status; this.detail = detail; }
}
/** Keep tokens on the server. The backend enforces actor roles and company scope. */
export class Gestoria {
          baseUrl        ;
          token        ;
  constructor(baseUrl        , token        ) {
    this.baseUrl = baseUrl; this.token = token;
    const url = new URL(baseUrl);
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Invalid service URL');
  }
  async request             (path        , body          , method = body === undefined ? 'GET' : 'POST')             {
    if (!path.startsWith('/api/') || path.includes('..') || path.includes('\\') || path.includes('#')) throw new Error('Invalid API path');
    const response = await fetch(new URL(path, this.baseUrl), {
      method, redirect: 'error', headers: { Authorization: `Bearer ${this.token}`, ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}) },
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(30000),
    });
    const result = await response.json();
    if (!response.ok) throw new GestoriaError(response.status, result.detail ?? result);
    return result     ;
  }
  companies() { return this.request('/api/companies'); }
  obligations(companyId        ) { return this.request(`/api/companies/${id(companyId)}/obligations`); }
  dashboard(companyId        , year        ) { if (!Number.isInteger(year) || year < 2000 || year > 2100) throw new Error('Invalid year'); return this.request(`/api/companies/${id(companyId)}/dashboard?year=${year}`); }
  calculate(companyId        , input                         ) { return this.request(`/api/companies/${id(companyId)}/tax-calculations`, input); }
  createReport(companyId        , year        ) { return this.request(`/api/companies/${id(companyId)}/reports`, { year }); }
  cases(companyId        ) { return this.request(`/api/companies/${id(companyId)}/cases`); }
  createCase(companyId        , draft                         ) { return this.request(`/api/companies/${id(companyId)}/cases`, draft); }
  propose(companyId        , revision        ) { return this.request(`/api/companies/${id(companyId)}/generate-plan`, { revision }); }
}
export function id(value        ) { if (!/^[a-f0-9]{32}$/.test(value)) throw new Error('Invalid identifier'); return value; }
