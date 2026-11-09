import type { Gestoria } from './index.js';
export type OdooErrorCode = 'auth'|'forbidden'|'not_found'|'validation'|'conflict'|'idempotency_conflict'|'unsupported'|'not_ready'|'timeout'|'provider_unavailable'|'reconciliation_required'|string;
export interface OdooFailure { code: OdooErrorCode; message: string; correlation_id: string; retryable: boolean; reconciliation_required?: boolean }
export interface Connection { connection_id: string; gestoria_company_id: string; tenant_id: string; provider: 'odoo_community'; provider_version: '19.0'; state: 'pending_validation'|'ready'|'degraded'|'disabled'; revision: number; capabilities: string[]; checked_at?: string; expires_at?: string }
export interface Health extends Connection { stale: boolean; evidence_hash?: string; unsupported: string[]; remote_publication: false; official_filing: false }
export interface JobReceipt { job_id: string; state: string }
export interface Job { id: string; company_id: string; connection_id: string; state: 'pending'|'running'|'succeeded'|'failed'|'reconciliation_required'|'blocked'; attempts: number; revision: number; correlation_id: string; result: unknown; error: OdooFailure|null }
export interface PartnerChange { name: string; email?: string; vat?: string; is_company?: boolean; remote_id?: number; expected_remote_write_date?: string }
export interface DraftProjection { invoice_draft_id: string; partner_id: number; journal_id: number; account_id: number; tax_ids: number[]; expected_draft_hash: string }
export interface Proposal { id: string; company_id: string; connection_id: string; revision: number; state: 'proposed'; proposal_hash: string; expires_at: string; diff: unknown; risk: string }
export interface Approval { id: string; company_id: string; proposal_id: string; proposal_hash: string; actor_id: string; actor_role: 'owner'|'reviewer'; expires_at: string }
export interface Commit { proposal_id: string; approval_id: string; expected_revision: number; idempotency_key: string }
export interface Operation { status: 'succeeded'|'reconciliation_required'|'blocked'; local_id: string; remote_id: number|null; reconciliation_required: boolean; retryable: boolean; source_hash?: string }
export interface Stage { id: string; company_id: string; connection_id: string; model: 'res.partner'|'account.move'; external_id: string; source_hash: string; mapping_version: 'odoo19-v1'; state: 'staged'|'mapping_blocked'|'imported'|'conflict'; warnings: string[]; normalized: unknown }
export interface Conflict { id: string; company_id: string; connection_id: string; revision: number; state: 'open'|'resolved'; reason: string; stage_id: string|null; marker_ids: string[] }
export declare class OdooError extends Error {
  status: number;
  failure: OdooFailure;
  constructor(status:number,failure:OdooFailure);
}
export declare class Odoo {
 constructor(client:Gestoria,companyId:string);
 health():Promise<Health>;
 capabilities():Promise<Health>;
 connect(server_ref:string):Promise<Connection>;
 validate(input:{revision:number;confirm_fiscal_identity?:boolean;notes?:string}):Promise<Connection>;
 disable(revision:number):Promise<Connection>;
 preview(resource:'partners'|'invoices',full:boolean,key:string):Promise<JobReceipt>;
 importStages(stagingIds:string[],key:string):Promise<JobReceipt>;
 job(jobId:string):Promise<Job>;
 staging():Promise<Stage[]>;
 conflicts():Promise<Conflict[]>;
 proposePartner(input:PartnerChange):Promise<Proposal>;
 proposeInvoice(input:DraftProjection):Promise<Proposal>;
 projectionInput(draftId:string):Promise<{invoice_draft_id:string;source_hash:string;totals:unknown;status:string}>;
 approve(proposalId:string,input:{revision:number;proposal_hash:string;notes:string}):Promise<Approval>;
 commitPartner(input:Commit):Promise<Operation>;
 commitInvoice(input:Commit):Promise<Operation>;
 reconcile(key:string):Promise<Operation>;
 resolve(conflictId:string,input:{revision:number;decision:'keep_local'|'supersede_local';notes:string}):Promise<Conflict>;
 attachmentMetadata(invoiceId:number):Promise<unknown[]>;
 downloadAttachment(invoiceId:number,attachmentId:number):Promise<unknown>;
 acknowledgeEvents(eventIds:string[]):Promise<{acknowledged:number}>;
 events():Promise<unknown[]>;
 briefing():Promise<unknown>;
 metrics():Promise<unknown>;
 auditIntegrity():Promise<unknown>;
}
