import { Gestoria, GestoriaError, id } from './index.js';
                                                                                                                                                                                                      
                                                                                                                                                    
                                                                                                                                                                                                                                                                                                          
                                                                                                                                                               
                                                             
                                                                                                                                                                                                                                                                         
                                                                                                                                                            
                                                                                                                                                                         
                                                                                                                                                                                                
                                                                                                                                                                              
                                                                                                                        
                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                            
export class OdooError extends Error {
  status        ; failure             ;
  constructor(status        , failure             ) { super(failure.message); this.status=status; this.failure=failure; }
}
function object(value         )                          { if (!value || typeof value!=='object' || Array.isArray(value)) throw new Error('Invalid Odoo DTO'); return value                          ; }
function keys(value         , allowed          ) { const v=object(value); if(Object.keys(v).some(k=>!allowed.includes(k)))throw new Error('Unknown operation field'); return v; }
function opaque(value        ) { if(!/^[a-zA-Z0-9_.:@/-]{1,160}$/.test(value))throw new Error('Invalid operation key'); return value; }
function positive(value        ) { if(!Number.isSafeInteger(value)||value<=0)throw new Error('Invalid remote id'); return value; }
function revision(value        ) { if(!Number.isSafeInteger(value)||value<0)throw new Error('Invalid revision'); return value; }
function proof(value        ) { if(!/^[a-f0-9]{64}$/.test(value))throw new Error('Invalid content hash'); return value; }
function response   (value         , field        )    { const v=object(value); if(!(field in v))throw new Error('Invalid provider contract response'); for(const key of ['id','job_id','connection_id','gestoria_company_id'])if(key in v)id(String(v[key])); if('revision' in v)revision(Number(v.revision)); for(const key of ['source_hash','proposal_hash'])if(key in v)proof(String(v[key])); if('state' in v&&(!['pending_validation','ready','degraded','disabled','pending','running','succeeded','failed','reconciliation_required','blocked','proposed','staged','mapping_blocked','imported','conflict','open','resolved'].includes(String(v.state))))throw new Error('Invalid operation state'); return value     ; }
/** Backend only. Actor tokens and tenant scopes are resolved by the host, never by a model prompt. */
export class Odoo {
          client          ;         root        ;
  constructor(client          , companyId        ) { this.client=client; this.root=`/api/companies/${id(companyId)}/integrations/odoo`; }
          async call   (path        , body          , field         )             {
    try { const value=await this.client.request(this.root+path,body); return field?response   (value,field):value     ; }
    catch(error) { if(error instanceof GestoriaError) {const raw=error.detail&&typeof error.detail==='object'&&!Array.isArray(error.detail)?error.detail                          :{};const failure             ={code:typeof raw.code==='string'?raw.code:'provider_unavailable',message:typeof raw.message==='string'?raw.message:'Integration request failed',correlation_id:typeof raw.correlation_id==='string'?raw.correlation_id:'',retryable:raw.retryable===true,reconciliation_required:raw.reconciliation_required===true};throw new OdooError(error.status,failure);} throw new OdooError(503,{code:'provider_unavailable',message:'Integration request could not be completed',correlation_id:'',retryable:false}); }
  }
  health() { return this.call        ('/health',undefined,'connection_id'); }
  capabilities() { return this.call        ('/capabilities',undefined,'connection_id'); }
  connect(server_ref        ) { return this.call            ('/connections',{server_ref:opaque(server_ref)},'connection_id'); }
  validate(input                                                                  ) { keys(input,['revision','confirm_fiscal_identity','notes']); revision(input.revision); return this.call            ('/connections/validate',input,'connection_id'); }
  disable(expectedRevision        ) { return this.call            ('/connections/disable',{revision:revision(expectedRevision)},'connection_id'); }
  preview(resource                      , full        , key       ) { if(!['partners','invoices'].includes(resource)||typeof full!=='boolean')throw new Error('Invalid preview');return this.call            ('/imports/preview',{resource,full,idempotency_key:opaque(key)},'job_id'); }
  importStages(stagingIds         ,key       ) {if(!Array.isArray(stagingIds)||stagingIds.length<1||stagingIds.length>200)throw new Error('Invalid stages');return this.call            ('/imports',{staging_ids:stagingIds.map(id),idempotency_key:opaque(key)},'job_id');}
  job(jobId       ) {return this.call     (`/jobs/${id(jobId)}`,undefined,'state');}
  async staging() {const value=await this.call         ('/staging');if(!Array.isArray(value))throw new Error('Invalid stages response');return value.map(x=>response       (x,'source_hash'));}
  async conflicts() {const value=await this.call         ('/conflicts');if(!Array.isArray(value))throw new Error('Invalid conflicts response');return value.map(x=>response          (x,'state'));}
  proposePartner(input              ) {keys(input,['name','email','vat','is_company','remote_id','expected_remote_write_date']);if(typeof input.name!=='string'||input.name.length<2||input.name.length>160)throw new Error('Invalid partner name');if(input.remote_id)positive(input.remote_id);return this.call          ('/partners/dry-run',input,'proposal_hash');}
  proposeInvoice(input                ) {keys(input,['invoice_draft_id','partner_id','journal_id','account_id','tax_ids','expected_draft_hash']);id(input.invoice_draft_id);[input.partner_id,input.journal_id,input.account_id].forEach(positive);if(!Array.isArray(input.tax_ids)||input.tax_ids.length>10)throw new Error('Invalid taxes');input.tax_ids.forEach(positive);proof(input.expected_draft_hash);return this.call          ('/invoice-drafts/dry-run',input,'proposal_hash');}
  projectionInput(draftId       ) {return this.call                                                                           (`/invoice-drafts/${id(draftId)}/projection-input`,undefined,'source_hash');}
  approve(proposalId       ,input                                                    ) {keys(input,['revision','proposal_hash','notes']);revision(input.revision);proof(input.proposal_hash);if(typeof input.notes!=='string'||input.notes.length<5)throw new Error('Review notes required');return this.call          (`/proposals/${id(proposalId)}/approve`,input,'proposal_hash');}
          commit(kind                            , input       ) {keys(input,['proposal_id','approval_id','expected_revision','idempotency_key']);id(input.proposal_id);id(input.approval_id);revision(input.expected_revision);opaque(input.idempotency_key);return this.call           (`/${kind}/commit`,input,'status');}
  commitPartner(input       ) {return this.commit('partners',input);}
  commitInvoice(input       ) {return this.commit('invoice-drafts',input);}
  reconcile(key       ) {return this.call           ('/writes/reconcile',{idempotency_key:opaque(key)},'status');}
  resolve(conflictId       ,input                                                                       ) {keys(input,['revision','decision','notes']);revision(input.revision);if(!['keep_local','supersede_local'].includes(input.decision)||typeof input.notes!=='string'||input.notes.length<5)throw new Error('Invalid conflict resolution');return this.call          (`/conflicts/${id(conflictId)}/resolve`,input,'state');}
  attachmentMetadata(invoiceId       ) {return this.call           (`/invoices/${positive(invoiceId)}/attachments`);}
  downloadAttachment(invoiceId       ,attachmentId       ) {return this.call         (`/invoices/${positive(invoiceId)}/attachments/download`,{attachment_id:positive(attachmentId)},'sha256');}
  acknowledgeEvents(eventIds         ) {if(!Array.isArray(eventIds)||eventIds.length<1||eventIds.length>200)throw new Error('Invalid event ids');return this.call                       ('/events/ack',{event_ids:eventIds.map(id)},'acknowledged');}
  events() {return this.call           ('/events');}
  briefing() {return this.call         ('/briefing',undefined,'source');}
  metrics() {return this.call         ('/metrics',undefined,'sample_size');}
  auditIntegrity() {return this.call         ('/audit-integrity',undefined,'valid');}
}
