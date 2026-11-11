import { Gestoria, GestoriaError, id } from './index.ts';
export type OdooErrorCode = 'auth'|'forbidden'|'not_found'|'validation'|'conflict'|'idempotency_conflict'|'unsupported'|'not_ready'|'timeout'|'provider_unavailable'|'reconciliation_required'|string;
export interface OdooFailure {
  code: OdooErrorCode;
  message: string;
  correlation_id: string;
  retryable: boolean;
  reconciliation_required?: boolean;
  category?: string;
  next_action?: string;
}
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
export class OdooError extends Error {
  status: number; failure: OdooFailure;
  constructor(status: number, failure: OdooFailure) { super(failure.message); this.status=status; this.failure=failure; }
}
function object(value: unknown): Record<string, unknown> { if (!value || typeof value!=='object' || Array.isArray(value)) throw new Error('Invalid Odoo DTO'); return value as Record<string,unknown>; }
function keys(value: unknown, allowed: string[]) { const v=object(value); if(Object.keys(v).some(k=>!allowed.includes(k)))throw new Error('Unknown operation field'); return v; }
function opaque(value: string) { if(!/^[a-zA-Z0-9_.:@/-]{1,160}$/.test(value))throw new Error('Invalid operation key'); return value; }
function positive(value: number) { if(!Number.isSafeInteger(value)||value<=0)throw new Error('Invalid remote id'); return value; }
function revision(value: number) { if(!Number.isSafeInteger(value)||value<0)throw new Error('Invalid revision'); return value; }
function proof(value: string) { if(!/^[a-f0-9]{64}$/.test(value))throw new Error('Invalid content hash'); return value; }
function response<T>(value: unknown, field: string): T { const v=object(value); if(!(field in v))throw new Error('Invalid provider contract response'); for(const key of ['id','job_id','connection_id','gestoria_company_id'])if(key in v)id(String(v[key])); if('revision' in v)revision(Number(v.revision)); for(const key of ['source_hash','proposal_hash'])if(key in v)proof(String(v[key])); if('state' in v&&(!['pending_validation','ready','degraded','disabled','pending','running','succeeded','failed','reconciliation_required','blocked','proposed','staged','mapping_blocked','imported','conflict','open','resolved'].includes(String(v.state))))throw new Error('Invalid operation state'); return value as T; }
/** Backend only. Actor tokens and tenant scopes are resolved by the host, never by a model prompt. */
export class Odoo {
  private client: Gestoria; private root: string;
  constructor(client: Gestoria, companyId: string) { this.client=client; this.root=`/api/companies/${id(companyId)}/integrations/odoo`; }
  private async call<T>(path: string, body?: unknown, field?: string): Promise<T> {
    try { const value=await this.client.request(this.root+path,body); return field?response<T>(value,field):value as T; }
    catch(error) { if(error instanceof GestoriaError) {const raw=error.detail&&typeof error.detail==='object'&&!Array.isArray(error.detail)?error.detail as Record<string,unknown>:{};const failure: OdooFailure={code:typeof raw.code==='string'?raw.code:'provider_unavailable',message:typeof raw.message==='string'?raw.message:'Integration request failed',correlation_id:typeof raw.correlation_id==='string'?raw.correlation_id:'',retryable:raw.retryable===true,reconciliation_required:raw.reconciliation_required===true,...(typeof raw.category==='string'?{category:raw.category}:{}),...(typeof raw.next_action==='string'?{next_action:raw.next_action}:{})};throw new OdooError(error.status,failure);} throw new OdooError(503,{code:'provider_unavailable',message:'Integration request could not be completed',correlation_id:'',retryable:false}); }
  }
  health() { return this.call<Health>('/health',undefined,'connection_id'); }
  capabilities() { return this.call<Health>('/capabilities',undefined,'connection_id'); }
  connect(server_ref: string) { return this.call<Connection>('/connections',{server_ref:opaque(server_ref)},'connection_id'); }
  validate(input: {revision:number;confirm_fiscal_identity?:boolean;notes?:string}) { keys(input,['revision','confirm_fiscal_identity','notes']); revision(input.revision); return this.call<Connection>('/connections/validate',input,'connection_id'); }
  disable(expectedRevision: number) { return this.call<Connection>('/connections/disable',{revision:revision(expectedRevision)},'connection_id'); }
  preview(resource:'partners'|'invoices', full:boolean, key:string) { if(!['partners','invoices'].includes(resource)||typeof full!=='boolean')throw new Error('Invalid preview');return this.call<JobReceipt>('/imports/preview',{resource,full,idempotency_key:opaque(key)},'job_id'); }
  importStages(stagingIds:string[],key:string) {if(!Array.isArray(stagingIds)||stagingIds.length<1||stagingIds.length>200)throw new Error('Invalid stages');return this.call<JobReceipt>('/imports',{staging_ids:stagingIds.map(id),idempotency_key:opaque(key)},'job_id');}
  job(jobId:string) {return this.call<Job>(`/jobs/${id(jobId)}`,undefined,'state');}
  async staging() {const value=await this.call<unknown>('/staging');if(!Array.isArray(value))throw new Error('Invalid stages response');return value.map(x=>response<Stage>(x,'source_hash'));}
  async conflicts() {const value=await this.call<unknown>('/conflicts');if(!Array.isArray(value))throw new Error('Invalid conflicts response');return value.map(x=>response<Conflict>(x,'state'));}
  proposePartner(input:PartnerChange) {keys(input,['name','email','vat','is_company','remote_id','expected_remote_write_date']);if(typeof input.name!=='string'||input.name.length<2||input.name.length>160)throw new Error('Invalid partner name');if(input.remote_id)positive(input.remote_id);return this.call<Proposal>('/partners/dry-run',input,'proposal_hash');}
  proposeInvoice(input:DraftProjection) {keys(input,['invoice_draft_id','partner_id','journal_id','account_id','tax_ids','expected_draft_hash']);id(input.invoice_draft_id);[input.partner_id,input.journal_id,input.account_id].forEach(positive);if(!Array.isArray(input.tax_ids)||input.tax_ids.length>10)throw new Error('Invalid taxes');input.tax_ids.forEach(positive);proof(input.expected_draft_hash);return this.call<Proposal>('/invoice-drafts/dry-run',input,'proposal_hash');}
  projectionInput(draftId:string) {return this.call<{invoice_draft_id:string;source_hash:string;totals:unknown;status:string}>(`/invoice-drafts/${id(draftId)}/projection-input`,undefined,'source_hash');}
  approve(proposalId:string,input:{revision:number;proposal_hash:string;notes:string}) {keys(input,['revision','proposal_hash','notes']);revision(input.revision);proof(input.proposal_hash);if(typeof input.notes!=='string'||input.notes.length<5)throw new Error('Review notes required');return this.call<Approval>(`/proposals/${id(proposalId)}/approve`,input,'proposal_hash');}
  private commit(kind:'partners'|'invoice-drafts', input:Commit) {keys(input,['proposal_id','approval_id','expected_revision','idempotency_key']);id(input.proposal_id);id(input.approval_id);revision(input.expected_revision);opaque(input.idempotency_key);return this.call<Operation>(`/${kind}/commit`,input,'status');}
  commitPartner(input:Commit) {return this.commit('partners',input);}
  commitInvoice(input:Commit) {return this.commit('invoice-drafts',input);}
  reconcile(key:string) {return this.call<Operation>('/writes/reconcile',{idempotency_key:opaque(key)},'status');}
  resolve(conflictId:string,input:{revision:number;decision:'keep_local'|'supersede_local';notes:string}) {keys(input,['revision','decision','notes']);revision(input.revision);if(!['keep_local','supersede_local'].includes(input.decision)||typeof input.notes!=='string'||input.notes.length<5)throw new Error('Invalid conflict resolution');return this.call<Conflict>(`/conflicts/${id(conflictId)}/resolve`,input,'state');}
  attachmentMetadata(invoiceId:number) {return this.call<unknown[]>(`/invoices/${positive(invoiceId)}/attachments`);}
  downloadAttachment(invoiceId:number,attachmentId:number) {return this.call<unknown>(`/invoices/${positive(invoiceId)}/attachments/download`,{attachment_id:positive(attachmentId)},'sha256');}
  acknowledgeEvents(eventIds:string[]) {if(!Array.isArray(eventIds)||eventIds.length<1||eventIds.length>200)throw new Error('Invalid event ids');return this.call<{acknowledged:number}>('/events/ack',{event_ids:eventIds.map(id)},'acknowledged');}
  events() {return this.call<unknown[]>('/events');}
  briefing() {return this.call<unknown>('/briefing',undefined,'source');}
  metrics() {return this.call<unknown>('/metrics',undefined,'sample_size');}
  auditIntegrity() {return this.call<unknown>('/audit-integrity',undefined,'valid');}
}
