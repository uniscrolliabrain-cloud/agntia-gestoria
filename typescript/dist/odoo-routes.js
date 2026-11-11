/** Exact business routes only; never allow provider model/method passthrough. */
const hex='[a-f0-9]{32}', prefix=`/api/companies/${hex}/integrations/odoo`;
const specs                        =[
 ['GET','(?:health|capabilities|staging|conflicts|audit-integrity|metrics|events|briefing)'],
 ['GET',`jobs/${hex}`],['GET',`invoice-drafts/${hex}/projection-input`],['GET','invoices/[1-9][0-9]*/attachments'],
 ['POST','connections(?:/validate|/disable)?'],['POST','imports(?:/preview)?'],
 ['POST',`conflicts/${hex}/resolve`],['POST',`proposals/${hex}/approve`],['POST',`records/${hex}/classification`],
 ['POST','(?:partners|invoice-drafts)/(?:dry-run|commit)'],['POST','events/ack'],['POST','writes/reconcile'],['POST','invoices/[1-9][0-9]*/attachments/download'],
];
export function allowedOdooRoute(method       ,path       ) {return specs.some(([verb,suffix])=>method===verb&&new RegExp(`^${prefix}/${suffix}$`).test(path));}
