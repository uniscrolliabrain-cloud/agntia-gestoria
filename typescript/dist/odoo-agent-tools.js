import { Odoo } from './odoo.js';
                                                                
/** No approval, classification, commit, arbitrary method, URL, tenant or credential tools. */
export function odooAgentTools(client      ) {
 return {
  odoo_connection_health: {description:'Read verified connection capability and freshness evidence.',execute:()=>client.health()},
  odoo_import_preview: {description:'Queue source extraction into staging; never approve tax records.',execute:(input                                                                     )=>client.preview(input.resource,input.full,input.idempotency_key)},
  odoo_list_unreviewed_invoices: {description:'Read staged source snapshots and mapping blockers.',execute:()=>client.staging()},
  odoo_import_staged: {description:'Queue an idempotent import as unverified economic facts.',execute:(input                                              )=>client.importStages(input.staging_ids,input.idempotency_key)},
  odoo_sync_status: {description:'Read the persisted state of a company-scoped job.',execute:(input                )=>client.job(input.job_id)},
  odoo_reconciliation_issues: {description:'Read open source discrepancies; does not resolve them.',execute:()=>client.conflicts()},
  odoo_propose_partner_change: {description:'Prepare an expiring proposal for human review; no remote write.',execute:(input              )=>client.proposePartner(input)},
  odoo_propose_invoice_draft: {description:'Compare draft totals and propose a draft-only projection; no publication.',execute:(input                )=>client.proposeInvoice(input)},
  odoo_briefing_evidence: {description:'Read actual counts and job outcomes for Laia; never invent activity.',execute:()=>client.briefing()},
 };
}
