import type {Odoo,PartnerChange,DraftProjection,Health,JobReceipt,Job,Stage,Conflict,Proposal} from './odoo.js';
type Tool<I,O>={description:string;execute:(input:I)=>Promise<O>};
type ReadTool<O>={description:string;execute:()=>Promise<O>};
export declare function odooAgentTools(client:Odoo):{
 odoo_connection_health:ReadTool<Health>;
 odoo_import_preview:Tool<{resource:'partners'|'invoices';full:boolean;idempotency_key:string},JobReceipt>;
 odoo_list_unreviewed_invoices:ReadTool<Stage[]>;
 odoo_import_staged:Tool<{staging_ids:string[];idempotency_key:string},JobReceipt>;
 odoo_sync_status:Tool<{job_id:string},Job>;
 odoo_reconciliation_issues:ReadTool<Conflict[]>;
 odoo_propose_partner_change:Tool<PartnerChange,Proposal>;
 odoo_propose_invoice_draft:Tool<DraftProjection,Proposal>;
 odoo_briefing_evidence:ReadTool<unknown>;
};
