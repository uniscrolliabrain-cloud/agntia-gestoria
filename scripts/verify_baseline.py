"""Inventory frozen C01 sources without importing the app or opening a database.

New integration files are allowed. Changes to any of the 43 frozen baseline
files are reported explicitly; future campaigns must update the policy through
review, rather than regenerating a baseline silently.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs/odoo-adapter/c01/baseline-inventory.json'
POLICY=ROOT/'docs/odoo-adapter/approved-source-changes.json'


def validate_changes(previous,current,policy):
    """Only accept exact, documented changes; the original manifest stays intact."""
    protected={'agntia_gestoria/engines.py','agntia_gestoria/rules.py','agntia_gestoria/territories.py','agntia_gestoria/tax.py','agntia_gestoria/data/legal_sources.json'}
    approved=policy.get('changes',{})
    if protected.intersection(approved):raise ValueError('Fiscal baseline cannot be exempted by this adapter policy')
    if not policy.get('authorization') or not policy.get('adr'):raise ValueError('Missing change authorization and ADR')
    if not (ROOT/policy['adr']).is_file():raise ValueError('Missing ADR file')
    for path,item in approved.items():
        if path not in previous or item.get('old_sha256')!=previous[path]:raise ValueError('Policy does not match frozen source: '+path)
        if current.get(path)!=item.get('new_sha256'):raise ValueError('Approved source changed again: '+path)
    unexpected=[path for path,value in current.items() if value!=previous[path] and path not in approved]
    if unexpected:raise ValueError('Frozen baseline files changed without explicit policy: '+', '.join(unexpected))
    return sorted(approved)


def inventory(paths):
    files=[];routes=[];python_api=[];typescript_api=[]
    for relative in sorted(paths):
        raw=(ROOT/relative).read_bytes()
        files.append({'path':relative,'bytes':len(raw),'lines':len(raw.splitlines()),'sha256':hashlib.sha256(raw).hexdigest()})
        text=raw.decode('utf-8')
        if relative.endswith('.py'):
            tree=ast.parse(text,filename=relative)
            for node in ast.walk(tree):
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    for decorator in node.decorator_list:
                        if not isinstance(decorator,ast.Call) or not isinstance(decorator.func,ast.Attribute) or decorator.func.attr not in ('get','post','put','delete','patch'):continue
                        if not decorator.args or not isinstance(decorator.args[0],ast.Constant):continue
                        roles=[]
                        for call in ast.walk(node):
                            if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='require_role':
                                roles.extend(ast.unparse(a) for a in call.args[1:])
                        routes.append({'method':decorator.func.attr.upper(),'path':decorator.args[0].value,'handler':node.name,'signature':ast.unparse(node.args),'file':relative,'line':node.lineno,'explicit_role_arguments':roles})
            for node in tree.body:
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):python_api.append({'file':relative,'name':node.name,'signature':ast.unparse(node.args)})
                elif isinstance(node,ast.ClassDef):
                    for method in node.body:
                        if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):python_api.append({'file':relative,'name':node.name+'.'+method.name,'signature':ast.unparse(method.args)})
        elif relative.endswith('.ts'):
            for number,line in enumerate(text.splitlines(),1):
                if re.match(r'\s*export\s+(declare\s+)?(class|function|type|interface)\b',line):typescript_api.append({'file':relative,'line':number,'declaration':line.split('{',1)[0].strip()})
    return {'schema_version':1,'files':files,'routes':sorted(routes,key=lambda r:(r['path'],r['method'])),'python_api':python_api,'typescript_exports':typescript_api}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-tree',help='Capture a Git tree into --output; never updates the committed manifest implicitly')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.capture_tree:
        if not args.output:parser.error('--capture-tree requires --output')
        entries=subprocess.check_output(['git','ls-tree','-rz','--full-tree',args.capture_tree],cwd=ROOT).split(b'\0')
        paths=[]
        for entry in entries:
            if not entry:continue
            header,path=entry.split(b'\t',1);mode,kind,sha=header.decode().split()
            if kind!='blob':continue
            relative=path.decode();raw=(ROOT/relative).read_bytes()
            actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if actual!=sha:raise SystemExit('Working file differs from supplied baseline tree: '+relative)
            paths.append(relative)
        result=inventory(paths);result['baseline_tree']=args.capture_tree
    else:
        expected=json.loads(MANIFEST.read_text())
        result=inventory([f['path'] for f in expected['files']]);result['baseline_tree']=expected['baseline_tree']
        previous={f['path']:f['sha256'] for f in expected['files']}
        policy=json.loads(POLICY.read_text()) if POLICY.exists() else {}
        changed=[f['path'] for f in result['files'] if f['sha256']!=previous[f['path']]]
        if changed or policy:
            if policy.get('baseline_tree')!=expected['baseline_tree']:raise SystemExit('Change policy targets another baseline')
            try:validate_changes(previous,{f['path']:f['sha256'] for f in result['files']},policy)
            except ValueError as exc:raise SystemExit(str(exc))
    if args.output:args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'baseline_tree':result['baseline_tree'],'verified_files':len(result['files']),'inventoried_routes':len(result['routes']),'status':'PASS'}))


if __name__=='__main__':main()
