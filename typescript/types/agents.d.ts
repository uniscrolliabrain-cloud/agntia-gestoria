import type { Gestoria } from './index.js';
type Tool<T> = { description: string; execute: (input: T) => Promise<unknown> };
type ReadTool = { description: string; execute: () => Promise<unknown> };
export declare function agentTools(client: Gestoria, companyId: string): {
 list_obligations: ReadTool;
 list_tax_records: ReadTool;
 create_tax_record: Tool<Record<string, unknown>>;
 prepare_tax_return: Tool<Record<string, unknown>>;
 list_tax_preparations: ReadTool;
 business_dashboard: Tool<{ year: number }>;
 calculate_tax: Tool<Record<string, unknown>>;
 generate_report: Tool<{ year: number }>;
 list_cases: ReadTool;
 create_case: Tool<Record<string, unknown>>;
 propose_plan: Tool<{ revision: number }>;
 submit_review: Tool<{ caseId: string; revision: number }>;
 close_reviewed_case: Tool<{ caseId: string; revision: number }>;
};
