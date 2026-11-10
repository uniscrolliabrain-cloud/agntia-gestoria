"""Executed by bootstrap via Odoo shell, administrative synthetic provisioning only.
Not a provider worker. Never run this against a customer database.
"""
import base64
import json
from datetime import datetime,timedelta

if env.cr.dbname not in ('agntia_test_a','agntia_test_b'):
    raise RuntimeError('Only named synthetic databases are permitted')
label='A' if env.cr.dbname.endswith('_a') else 'B'
if env['res.users'].search_count([('login','=','agntia_fixture_bot')]):
    raise RuntimeError('Fixture already exists; no implicit credential rotation or reset')
company=env.company
country=env.ref('base.es')
company.write({
    'name':'Agntia synthetic fixture '+label,
    'country_id':country.id,
    'account_fiscal_country_id':country.id,
    'currency_id':env.ref('base.EUR').id,
    'vat':False,
    'tax_calculation_rounding_method':'round_per_line',
})
def account(code,name,kind,reconcile=False):
    return env['account.account'].create({'code':code,'name':name,'account_type':kind,'company_ids':[(6,0,[company.id])],'reconcile':reconcile})
income=account('700991','Synthetic revenue','income')
expense=account('629991','Synthetic expense','expense')
receivable=account('430991','Synthetic receivable','asset_receivable',True)
payable=account('400991','Synthetic payable','liability_payable',True)
journal=env['account.journal'].create({'name':'Synthetic sales','code':'AGT','type':'sale','company_id':company.id,'default_account_id':income.id})
partner=env['res.partner'].create({'name':'Synthetic customer '+label,'company_id':company.id,'email':'synthetic-'+label.lower()+'@example.invalid','property_account_receivable_id':receivable.id,'property_account_payable_id':payable.id})
rate=21 if label=='A' else 7
group=env['account.tax.group'].create({'name':'Synthetic tax group '+label,'company_id':company.id,'country_id':country.id})
tax=env['account.tax'].create({'name':'Synthetic '+('IVA 21' if label=='A' else 'IGIC 7'),'company_id':company.id,'tax_group_id':group.id,'amount_type':'percent','amount':rate,'type_tax_use':'sale','tax_exigibility':'on_invoice','price_include_override':'tax_excluded'})
move=env['account.move'].create({'move_type':'out_invoice','company_id':company.id,'partner_id':partner.id,'journal_id':journal.id,'invoice_date':'2026-04-10','invoice_line_ids':[(0,0,{'name':'Synthetic service','quantity':1,'price_unit':100,'account_id':income.id,'tax_ids':[(6,0,[tax.id])]} )]})
if move.state!='draft':raise RuntimeError('No posted invoice permitted')
attachment=env['ir.attachment'].create({'name':'synthetic-proof.pdf','type':'binary','datas':base64.b64encode(b'%PDF-1.7\nSYNTHETIC FIXTURE ONLY\n'),'mimetype':'application/pdf','res_model':'account.move','res_id':move.id,'company_id':company.id})
bot=env['res.users'].with_context(no_reset_password=True).create({'name':'Synthetic integration bot '+label,'login':'agntia_fixture_bot','email':'bot-'+label.lower()+'@example.invalid','company_id':company.id,'company_ids':[(6,0,[company.id])],'group_ids':[(6,0,[env.ref('agntia_bridge.group_integration').id])]})
if bot.has_group('base.group_system') or bot.has_group('account.group_account_invoice'):
    raise RuntimeError('Bot privileges unexpectedly broad')
key=env['res.users.apikeys'].with_user(bot)._generate('rpc','agntia-synthetic-lab',datetime.utcnow()+timedelta(days=7))
result={'database':env.cr.dbname,'instance_id':env.ref('agntia_bridge.database_instance').token,'company_id':company.id,'bot_uid':bot.id,'api_key':key,'partner_id':partner.id,'journal_id':journal.id,'account_id':income.id,'expense_account_id':expense.id,'tax_id':tax.id,'tax_rate':str(rate),'invoice_id':move.id,'attachment_id':attachment.id}
env.cr.commit()
print('AGNTIA_FIXTURE_RESULT:'+json.dumps(result))
