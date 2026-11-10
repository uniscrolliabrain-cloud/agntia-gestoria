"""Own LGPL-3 code. Atomic operations; no sudo and no generic ORM executor."""
import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
from odoo import api,fields,models,release
from odoo.exceptions import AccessError,ValidationError

_WRITE_TOKEN=object()

def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def hash_(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def money(value):return str(Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


class Instance(models.Model):
    _name='agntia.bridge.instance'
    _description='Agntia database instance identity'
    token=fields.Char(default=lambda self:uuid.uuid4().hex,required=True,readonly=True)


class Operation(models.Model):
    _name='agntia.bridge.operation'
    _description='Agntia atomic operation ledger'
    operation_key=fields.Char(required=True,index=True)
    request_hash=fields.Char(required=True)
    company_id=fields.Many2one('res.company',required=True,index=True)
    result_json=fields.Text(required=True)
    _key_unique=models.Constraint('UNIQUE(operation_key)','Operation identity must be unique')

    @api.model_create_multi
    def create(self,vals_list):
        if self.env.user.has_group('agntia_bridge.group_integration') and self.env.context.get('_agntia_internal_write') is not _WRITE_TOKEN:raise AccessError('Bridge ledger is private')
        return super().create(vals_list)
    def write(self,vals):
        if self.env.user.has_group('agntia_bridge.group_integration'):raise AccessError('Immutable bridge ledger')
        return super().write(vals)
    def unlink(self):
        if self.env.user.has_group('agntia_bridge.group_integration'):raise AccessError('Immutable bridge ledger')
        return super().unlink()


class Bridge(models.AbstractModel):
    _name='agntia.bridge'
    _description='Closed business operations for Agntia'

    def _scope(self,company_id):
        if not self.env.user.has_group('agntia_bridge.group_integration') or self.env.su or self.env.user.id==1:raise AccessError('Restricted integration principal required')
        if type(company_id)!=int or company_id not in self.env.user.company_ids.ids or self.env.context.get('allowed_company_ids')!=[company_id]:raise AccessError('Invalid integration company scope')
        return self.env['res.company'].browse(company_id).exists()

    @api.model
    def server_info(self,company_id):
        company=self._scope(company_id)
        instance=self.env['agntia.bridge.instance'].search([],limit=2)
        if len(instance)!=1:raise ValidationError('Database instance must be provisioned exactly once')
        names=['res.partner','account.move','account.move.line','account.tax','account.journal','account.account','ir.attachment']
        readable={n:n in self.env and self.env[n].has_access('read') for n in names}
        writable={n:n in self.env and self.env[n].has_access('create') and self.env[n].has_access('write') for n in ('res.partner','account.move')}
        module_model=self.env['ir.module.module'];version='installed_version' if 'installed_version' in module_model._fields else 'latest_version'
        modules=module_model.search_read([('name','in',['base','rpc','account','contacts','l10n_es','agntia_bridge','agntia_bridge_account','web_enterprise']),('state','=','installed')],['name',version])
        try:source_revision=Path('/opt/agntia-odoo-source-sha').read_text().strip()
        except OSError:source_revision=None
        return {'source_revision':source_revision,'enterprise_installed':any(r['name']=='web_enterprise' for r in modules),'version':release.series,'bridge_version':'1.0','instance_id':instance.token,'uid':self.env.user.id,'superuser':bool(self.env.su),'settings_admin':self.env.user.has_group('base.group_system'),'company_id':company.id,'company_vat':company.vat or '', 'allowed_company_ids':self.env.user.company_ids.ids,'read_access':readable,'write_access':writable,'modules':{r['name']:r.get(version) for r in modules},'server_now':fields.Datetime.to_string(fields.Datetime.now())}

    @api.model
    def invoice_snapshots(self,company_id,invoice_ids):
        ids=invoice_ids
        self._scope(company_id)
        if not isinstance(ids,list) or len(ids)>100 or len(set(ids))!=len(ids) or any(type(i)!=int or i<=0 for i in ids):raise ValidationError('Invalid invoice ids')
        if 'account.move' not in self.env:raise ValidationError('Accounting is not installed')
        moves=self.env['account.move'].search([('id','in',ids),('company_id','=',company_id),('move_type','in',['out_invoice','in_invoice','out_refund','in_refund'])],order='id')
        if set(moves.ids)!=set(ids):raise AccessError('Invoice set is inaccessible')
        result=[]
        for move in moves:
            move.check_access('read')
            lines=[]
            for line in move.invoice_line_ids.sorted(lambda l:(l.sequence,l.id)):
                line.check_access('read')
                taxes=[]
                for tax in line.tax_ids:
                    if tax.company_id.id!=company_id:raise AccessError('Tax company differs')
                    taxes.append({'id':tax.id,'company_id':company_id,'amount':str(tax.amount),'amount_type':tax.amount_type,'type_tax_use':tax.type_tax_use,'price_include':bool(tax.price_include),'children_tax_ids':tax.children_tax_ids.ids,'write_date':fields.Datetime.to_string(tax.write_date)})
                lines.append({'id':line.id,'move_id':move.id,'company_id':company_id,'display_type':line.display_type,'name':line.name or '', 'quantity':str(line.quantity),'price_unit':str(line.price_unit),'discount':str(line.discount),'price_subtotal':str(line.price_subtotal),'price_total':str(line.price_total),'taxes':taxes})
            result.append({'move':{'id':move.id,'company_id':company_id,'move_type':move.move_type,'state':move.state,'currency':move.currency_id.name,'invoice_date':fields.Date.to_string(move.invoice_date) if move.invoice_date else None,'amount_untaxed':str(move.amount_untaxed),'amount_tax':str(move.amount_tax),'amount_total':str(move.amount_total),'partner_name':move.partner_id.name or '', 'fiscal_position_id':move.fiscal_position_id.id or None,'cash_basis':any(t.tax_exigibility=='on_payment' for t in move.invoice_line_ids.tax_ids),'write_date':fields.Datetime.to_string(move.write_date)},'lines':lines})
        return result

    def _invoice_payload(self,company_id,payload):
        company=self._scope(company_id)
        expected={'kind','local_draft_id','partner_id','journal_id','account_id','tax_ids','invoice_date','lines','expected_totals','currency'}
        if not isinstance(payload,dict) or set(payload)!=expected or payload['kind']!='invoice_draft' or payload['currency']!='EUR':raise ValidationError('Invalid draft projection')
        if 'account.move' not in self.env:raise ValidationError('Accounting not installed')
        for name in ('partner_id','journal_id','account_id'):
            if type(payload[name])!=int or payload[name]<=0:raise ValidationError('Invalid relational identifier')
        partner=self.env['res.partner'].search([('id','=',payload['partner_id']),('company_id','=',company_id)],limit=1)
        journal=self.env['account.journal'].search([('id','=',payload['journal_id']),('company_id','=',company_id),('type','=','sale')],limit=1)
        account=self.env['account.account'].search([('id','=',payload['account_id']),('company_ids','in',[company_id]),('account_type','in',['income','income_other'])],limit=1)
        if not partner or not journal or not account:raise AccessError('Projection configuration out of scope')
        if partner.property_account_position_id:raise ValidationError('Fiscal position not supported by initial draft projection')
        currency=journal.currency_id or company.currency_id
        if currency.name!='EUR' or company.currency_id.name!='EUR' or company.tax_calculation_rounding_method!='round_per_line':raise ValidationError('Only EUR and line rounding are supported')
        ids=payload['tax_ids']
        if not isinstance(ids,list) or len(ids)>1 or any(type(i)!=int or i<=0 for i in ids):raise ValidationError('Single explicit tax required')
        taxes=self.env['account.tax'].search([('id','in',ids),('company_id','=',company_id),('type_tax_use','=','sale')])
        if set(taxes.ids)!=set(ids) or any(t.amount_type!='percent' or t.price_include or t.children_tax_ids or t.tax_exigibility!='on_invoice' for t in taxes):raise ValidationError('Unsupported tax composition')
        if not isinstance(payload['lines'],list) or not 1<=len(payload['lines'])<=200:raise ValidationError('Invalid lines')
        base=Decimal(0);tax_total=Decimal(0);total=Decimal(0);commands=[]
        for line in payload['lines']:
            if not isinstance(line,dict) or set(line)!={'name','quantity','price_unit'} or not isinstance(line['name'],str) or len(line['name'])>500:raise ValidationError('Invalid line fields')
            try:qty=Decimal(line['quantity']);price=Decimal(line['price_unit'])
            except Exception:raise ValidationError('Invalid decimal amounts') from None
            if not qty.is_finite() or not price.is_finite() or not 0<qty<=1000000 or not 0<=price<=100000000:raise ValidationError('Invalid decimal range')
            computed=taxes.compute_all(float(price),currency=currency,quantity=float(qty),partner=partner,rounding_method='round_per_line')
            b=Decimal(money(computed['total_excluded']));t=Decimal(money(computed['total_included']))
            base+=b;total+=t;tax_total+=t-b
            commands.append((0,0,{'name':line['name'],'quantity':float(qty),'price_unit':float(price),'account_id':account.id,'tax_ids':[(6,0,taxes.ids)]}))
        quote={'base':money(base),'tax':money(tax_total),'total':money(total)}
        expected_totals=payload['expected_totals']
        if not isinstance(expected_totals,dict) or any(quote[k]!=money(expected_totals.get(k,'NaN')) for k in quote):raise ValidationError('Expected totals differ from Odoo')
        values={'move_type':'out_invoice','company_id':company_id,'partner_id':partner.id,'journal_id':journal.id,'currency_id':currency.id,'invoice_date':payload['invoice_date'],'invoice_line_ids':commands,'state':'draft'}
        return values,quote

    @api.model
    def preview_invoice(self,company_id,payload):
        # Pure tax calculation and reads; never create/rollback a draft just for dry-run.
        values,quote=self._invoice_payload(company_id,payload)
        return quote

    def _verify_authorization(self,company_id,operation_key,request_hash,authorization):
        if not isinstance(authorization,dict) or set(authorization)!={'claims','signature'}:raise AccessError('Signed approval required')
        claims=authorization['claims']
        if not isinstance(claims,dict) or set(claims)!={'instance_id','company_id','operation_key','request_hash','approval_id','approved_by','expires_at'}:raise AccessError('Invalid approval claims')
        instance=self.env['agntia.bridge.instance'].search([],limit=2)
        if len(instance)!=1 or claims['instance_id']!=instance.token:raise AccessError('Approval database identity differs')
        if claims['company_id']!=company_id or claims['operation_key']!=operation_key or claims['request_hash']!=request_hash or type(claims['expires_at'])!=int or not time.time()<claims['expires_at']<=time.time()+901:raise AccessError('Approval scope or expiry differs')
        try:
            path=os.getenv('AGNTIA_BRIDGE_SIGNING_KEY_FILE','/run/secrets/agntia_bridge_signing_key');key=Path(path).read_bytes().strip()
        except OSError:raise AccessError('Approval verifier unavailable') from None
        if len(key)<32:raise AccessError('Approval verifier unavailable')
        signature=hmac.new(key,canonical(claims).encode(),hashlib.sha256).hexdigest()
        if not isinstance(authorization['signature'],str) or not hmac.compare_digest(signature,authorization['signature']):raise AccessError('Invalid approval signature')

    @api.model
    def execute_approved(self,company_id,operation_key,request_hash,payload,authorization):
        self._scope(company_id)
        if not isinstance(operation_key,str) or len(operation_key)!=64 or not isinstance(request_hash,str) or hash_(payload)!=request_hash:raise ValidationError('Invalid operation proof')
        self._verify_authorization(company_id,operation_key,request_hash,authorization)
        lock=int.from_bytes(hashlib.sha256(operation_key.encode()).digest()[:8],'big',signed=True)
        self.env.cr.execute('SELECT pg_advisory_xact_lock(%s)',[lock])
        ledger=self.env['agntia.bridge.operation']
        prior=ledger.search([('operation_key','=',operation_key)],limit=1)
        if prior:
            if prior.company_id.id!=company_id or prior.request_hash!=request_hash:raise AccessError('Operation identity collision')
            return json.loads(prior.result_json)
        env=self.with_context(_agntia_internal_write=_WRITE_TOKEN).env
        kind=payload.get('kind')
        if kind=='partner':
            if set(payload)!={'kind','remote_id','expected_write_date','values'} or not isinstance(payload['values'],dict) or set(payload['values'])!={'name','email','vat','is_company'}:raise ValidationError('Invalid partner change')
            if not isinstance(payload['values']['name'],str) or not 2<=len(payload['values']['name'])<=160 or len(payload['values']['email'])>254 or len(payload['values']['vat'])>40 or type(payload['values']['is_company'])!=bool:raise ValidationError('Invalid partner values')
            if payload['remote_id']:
                if type(payload['remote_id'])!=int:raise ValidationError('Invalid partner identity')
                record=env['res.partner'].search([('id','=',payload['remote_id']),('company_id','=',company_id)],limit=1)
                if not record:raise AccessError('Partner not accessible')
                self.env.cr.execute('SELECT id FROM res_partner WHERE id=%s FOR UPDATE',[record.id]);record.invalidate_recordset(['write_date'])
                if fields.Datetime.to_string(record.write_date)!=payload['expected_write_date']:raise ValidationError('Partner revision changed')
                record.write(payload['values'])
            else:record=env['res.partner'].create({**payload['values'],'company_id':company_id})
            result={'kind':'partner','remote_id':record.id,'company_id':company_id,'request_hash':request_hash,'write_date':fields.Datetime.to_string(record.write_date)}
        elif kind=='invoice_draft':
            values,quote=self._invoice_payload(company_id,payload)
            record=env['account.move'].create(values)
            if record.state!='draft' or record.name not in (False,'/') or record.posted_before:raise ValidationError('Draft state invariant violated')
            actual={'base':money(record.amount_untaxed),'tax':money(record.amount_tax),'total':money(record.amount_total)}
            if actual!=quote:raise ValidationError('Created draft totals differ; entire operation rolled back')
            result={'kind':'invoice_draft','remote_id':record.id,'company_id':company_id,'request_hash':request_hash,'state':'draft','totals':actual,'write_date':fields.Datetime.to_string(record.write_date)}
        else:raise ValidationError('Unsupported operation')
        env['agntia.bridge.operation'].create({'operation_key':operation_key,'request_hash':request_hash,'company_id':company_id,'result_json':canonical(result)})
        return result

    @api.model
    def operation_status(self,company_id,operation_key):
        self._scope(company_id)
        if not isinstance(operation_key,str) or len(operation_key)!=64:raise ValidationError('Invalid operation key')
        record=self.env['agntia.bridge.operation'].search([('operation_key','=',operation_key),('company_id','=',company_id)],limit=1)
        return json.loads(record.result_json) if record else False

    def _invoice(self,company_id,invoice_id):
        self._scope(company_id)
        if type(invoice_id)!=int or invoice_id<=0 or 'account.move' not in self.env:raise ValidationError('Invalid invoice')
        invoice=self.env['account.move'].search([('id','=',invoice_id),('company_id','=',company_id),('move_type','in',['out_invoice','in_invoice','out_refund','in_refund'])],limit=1)
        if not invoice:raise AccessError('Invoice inaccessible')
        return invoice

    @api.model
    def attachment_metadata(self,company_id,invoice_id):
        self._invoice(company_id,invoice_id)
        records=self.env['ir.attachment'].search([('res_model','=','account.move'),('res_id','=',invoice_id),('company_id','in',[False,company_id]),('type','=','binary')],limit=101)
        if len(records)>100:raise ValidationError('Too many attachments')
        return [{'id':r.id,'invoice_id':invoice_id,'name':r.name,'size':r.file_size,'mimetype':r.mimetype,'checksum':r.checksum} for r in records]

    @api.model
    def attachment_content(self,company_id,invoice_id,attachment_id):
        self._invoice(company_id,invoice_id)
        if type(attachment_id)!=int or attachment_id<=0:raise ValidationError('Invalid attachment')
        record=self.env['ir.attachment'].search([('id','=',attachment_id),('res_model','=','account.move'),('res_id','=',invoice_id),('company_id','in',[False,company_id]),('type','=','binary')],limit=1)
        if not record or record.file_size>4*1024*1024:raise AccessError('Attachment unavailable or too large')
        data=base64.b64decode(record.datas or b'',validate=True)
        if not data or len(data)>4*1024*1024:raise ValidationError('Invalid attachment size')
        return {'id':record.id,'company_id':company_id,'invoice_id':invoice_id,'name':record.name,'data':base64.b64encode(data).decode(),'sha256':hashlib.sha256(data).hexdigest()}
