import test from 'node:test';
import assert from 'node:assert/strict';
import {Gestoria} from '../dist/index.js';
import {Odoo,OdooError} from '../dist/odoo.js';
import {odooAgentTools} from '../dist/odoo-agent-tools.js';
import {allowedOdooRoute} from '../dist/odoo-routes.js';
const cid='a'.repeat(32), id='b'.repeat(32);
test('Odoo routes are exact and never an ORM passthrough',()=>{
 const p=`/api/companies/${cid}/integrations/odoo`;
 assert.equal(allowedOdooRoute('GET',p+'/health'),true);
 for(const [verb,path] of [['POST','/res.partner/create'],['POST','/account.move/action_post'],['PUT','/partners/commit'],['GET','/health/extra'],['POST','/execute']])assert.equal(allowedOdooRoute(verb,p+path),false);
});
test('Agent tools cannot approve, classify or commit',()=>{
 const tools=odooAgentTools(new Odoo(new Gestoria('http://localhost:8010','fixture'),cid));
 assert.ok(tools.odoo_propose_invoice_draft);
 assert.equal(Object.keys(tools).some(k=>/approve|commit|classify|execute_anything/.test(k)),false);
});
test('Runtime validators reject unknown context before fetch',async()=>{
 let calls=0;const original=globalThis.fetch;globalThis.fetch=async()=>{calls++;throw Error('Unexpected')};
 try{const client=new Odoo(new Gestoria('http://localhost:8010','fixture'),cid);assert.throws(()=>client.proposePartner({name:'Fixture',context:{allowed_company_ids:[2]}}));assert.equal(calls,0);}finally{globalThis.fetch=original}
});
test('Scoped operation and normalized errors',async()=>{
 const original=globalThis.fetch;
 globalThis.fetch=async(url)=>{assert.equal(String(url),`http://localhost:8010/api/companies/${cid}/integrations/odoo/health`);return {ok:false,status:424,json:async()=>({code:'unsupported',message:'Not configured',correlation_id:id,retryable:false})}};
 try{const client=new Odoo(new Gestoria('http://localhost:8010','fixture'),cid);await assert.rejects(client.health(),e=>e instanceof OdooError&&e.failure.code==='unsupported');}finally{globalThis.fetch=original}
});
