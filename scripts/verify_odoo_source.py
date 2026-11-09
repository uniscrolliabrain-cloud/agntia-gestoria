"""Verify pinned Odoo source contracts without importing or starting Odoo.
This is static verification, never evidence of an installed capability.
"""
import argparse
import ast
import csv
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',required=True,type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    lock=json.loads((ROOT/'infra/odoo/upstream-lock.json').read_text())
    sources={};checks=[]
    def check(name,condition,reference):
        if not condition:raise SystemExit('Source contract changed: '+name+' ('+reference+')')
        checks.append({'name':name,'status':'PASS','reference':reference})
    for item in lock['sources']:
        if item['repository']!='odoo/odoo':continue
        path=item['path'];raw=(args.source_root/path).read_bytes()
        check('sha256:'+path,hashlib.sha256(raw).hexdigest()==item['sha256'],item['url'])
        sources[path]=raw.decode('utf-8')
    def tree(path):return ast.parse(sources[path],filename=path)
    def fields(path,model):
        for cls in tree(path).body:
            if not isinstance(cls,ast.ClassDef):continue
            names={}
            for node in cls.body:
                if isinstance(node,ast.Assign):
                    for target in node.targets:
                        if isinstance(target,ast.Name):names[target.id]=node.value
                elif isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name):names[node.target.id]=node.value
            if isinstance(names.get('_name'),ast.Constant) and names['_name'].value==model:return names
        raise SystemExit('Missing model '+model)
    rpc=tree('addons/rpc/controllers/json2.py')
    methods=[n for n in ast.walk(rpc) if isinstance(n,ast.FunctionDef) and n.name=='web_json_2_rpc']
    check('JSON2 public handler exists',len(methods)==1,'addons/rpc/controllers/json2.py')
    rpc_method=methods[0];routes=[d for d in rpc_method.decorator_list if isinstance(d,ast.Call)]
    route=next(d for d in routes if isinstance(d.func,ast.Attribute) and d.func.attr=='route')
    options={k.arg:ast.literal_eval(k.value) for k in route.keywords if k.arg in ('methods','auth','save_session')}
    check('JSON2 bearer POST without session',options=={'methods':['POST'],'auth':'bearer','save_session':False},'addons/rpc/controllers/json2.py:49')
    calls=[n for n in ast.walk(rpc_method) if isinstance(n,ast.Call)]
    check('JSON2 resolves public methods',any(isinstance(n.func,ast.Name) and n.func.id=='get_public_method' for n in calls),'addons/rpc/controllers/json2.py')
    check('JSON2 handler has no sudo call',not any(isinstance(n.func,ast.Attribute) and n.func.attr=='sudo' for n in calls),'addons/rpc/controllers/json2.py')
    move=fields('addons/account/models/account_move.py','account.move')
    check('Invoice fields exist',set(['state','move_type','company_id','currency_id','invoice_line_ids','line_ids','journal_id','invoice_date','amount_total','amount_tax','amount_untaxed','partner_id'])<=move.keys(),'addons/account/models/account_move.py')
    def selection(call):
        return next(ast.literal_eval(k.value) for k in call.keywords if k.arg=='selection')
    check('Move states include draft and posted',{'draft','posted'}<=set(x[0] for x in selection(move['state'])),'account.move.state')
    check('Invoice and refund move types exist',{'entry','out_invoice','in_invoice','out_refund','in_refund'}<=set(x[0] for x in selection(move['move_type'])),'account.move.move_type')
    domain=next(ast.literal_eval(k.value) for k in move['invoice_line_ids'].keywords if k.arg=='domain')
    check('Invoice lines include sections, not just products',domain==[('display_type','in',('product','line_section','line_subsection','line_note'))],'account.move.invoice_line_ids')
    line=fields('addons/account/models/account_move_line.py','account.move.line')
    check('Technical line kinds must be excluded',{'product','tax','payment_term','rounding','line_note','line_section'}<=set(x[0] for x in selection(line['display_type'])),'account.move.line.display_type')
    tax=fields('addons/account/models/account_tax.py','account.tax')
    check('Taxes are not only percentage',{'group','fixed','percent','division'}<=set(x[0] for x in selection(tax['amount_type'])),'account.tax.amount_type')
    check('Tax company and price-included fields exist',{'company_id','amount','type_tax_use','price_include','children_tax_ids'}<=tax.keys(),'account.tax')
    account=fields('addons/account/models/account_account.py','account.account')
    check('Odoo19 account uses plural company_ids','company_ids' in account and 'company_id' not in account,'account.account')
    partner=fields('odoo/addons/base/models/res_partner.py','res.partner')
    check('Partner identification fields exist',{'company_id','country_id','vat','email','is_company','name'}<=partner.keys(),'res.partner')
    xml=ET.fromstring(sources['odoo/addons/base/security/base_security.xml'])
    rule=xml.find(".//record[@id='res_partner_rule']/field[@name='domain_force']")
    check('Partner rule has shared and internal-user exceptions',rule is not None and "('company_id', '=', False)" in rule.text and "('partner_share', '=', False)" in rule.text,'base_security.xml:res_partner_rule')
    acl=list(csv.DictReader(io.StringIO(sources['addons/account/security/ir.model.access.csv'])))
    readonly=next(r for r in acl if r['id']=='access_account_move_readonly')
    check('Read-only move ACL is read-only',[readonly[k] for k in ('perm_read','perm_write','perm_create','perm_unlink')]==['1','0','0','0'],'account/security/ir.model.access.csv')
    for module,path in [('account','addons/account/__manifest__.py'),('contacts','addons/contacts/__manifest__.py'),('l10n_es','addons/l10n_es/__manifest__.py'),('base','odoo/addons/base/__manifest__.py'),('rpc','addons/rpc/__manifest__.py')]:
        manifest=ast.literal_eval(tree(path).body[0].value)
        check(module+' license declared LGPL-3',manifest.get('license')=='LGPL-3',path)
        if module=='l10n_es':
            check('Spanish addon depends on account','account' in manifest['depends'],path)
            check('Spanish addon lists mod420 data','data/mod420.xml' in manifest['data'],path)
    result={'schema_version':1,'upstream_commit':lock['upstream']['commit'],'verification':'static_source_only','check_count':len(checks),'checks':checks,'runtime_capabilities':'NOT VERIFIED','enabled_capabilities':[]}
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'static_checks':len(checks),'status':'PASS','runtime':'NOT VERIFIED'}))


if __name__=='__main__':main()
