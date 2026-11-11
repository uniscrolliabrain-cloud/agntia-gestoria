import { Gestoria, id } from './index.js';
/** Bind a company-scoped token with role agent. Never use an owner/reviewer token. */
export function agentTools(client          , companyId        ) {
  const root = `/api/companies/${id(companyId)}`;
  return {
    list_obligations: { description: 'Read sourced proposals and missing facts.', execute: () => client.obligations(companyId) },
    list_tax_records: { description: 'Read economic records; their classifications remain unverified.', execute: () => client.request(`${root}/tax-records`) },
    create_tax_record: { description: 'Store an economic record with a unique external reference and optional document links.', execute: (record                         ) => client.request(`${root}/tax-records`, record) },
    prepare_tax_return: { description: 'Create a preparation snapshot. Does not calculate official boxes or submit a return.', execute: (input                         ) => client.request(`${root}/tax-preparations`, input) },
    list_tax_preparations: { description: 'Read preparations, blockers and stale-data indicators.', execute: () => client.request(`${root}/tax-preparations`) },
    business_dashboard: { description: 'Read explainable metrics and data-quality findings from company records.', execute: ({ year }                  ) => client.dashboard(companyId, year) },
    calculate_tax: { description: 'Calculate supported AEAT 2026 cases with reviewed records. Rejects unsupported regimes and incomplete data.', execute: (input                         ) => client.calculate(companyId, input) },
    generate_report: { description: 'Save a report snapshot for PDF, PPTX, SVG and HTML export.', execute: ({ year }                  ) => client.createReport(companyId, year) },
    list_cases: { description: 'Read internal cases.', execute: () => client.cases(companyId) },
    create_case: { description: 'Prepare a draft, never a governmental filing.', execute: (draft                         ) => client.createCase(companyId, draft) },
    propose_plan: { description: 'Generate non-overwriting draft cases from current company facts.', execute: ({ revision }                      ) => client.propose(companyId, revision) },
    submit_review: { description: 'Ask for human review of a specific revision.', execute: ({ caseId, revision }                                      ) => client.request(`${root}/cases/${id(caseId)}/submit-review`, { revision }) },
  };
}
