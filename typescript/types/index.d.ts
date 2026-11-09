export declare class GestoriaError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown);
}
export declare class Gestoria {
  constructor(baseUrl: string, token: string);
  request<T = unknown>(path: string, body?: unknown, method?: string): Promise<T>;
  companies(): Promise<unknown>;
  obligations(companyId: string): Promise<unknown>;
  dashboard(companyId: string, year: number): Promise<unknown>;
  calculate(companyId: string, input: Record<string, unknown>): Promise<unknown>;
  createReport(companyId: string, year: number): Promise<unknown>;
  cases(companyId: string): Promise<unknown>;
  createCase(companyId: string, draft: Record<string, unknown>): Promise<unknown>;
  propose(companyId: string, revision: number): Promise<unknown>;
}
export declare function id(value: string): string;
