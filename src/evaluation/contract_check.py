"""Non-repairing diagnostic pre-check for generated POSG source."""
from __future__ import annotations
import ast
from typing import Any
REQUIRED={'players':['self'],'initial_state':['self'],'legal_actions':['self','state','player'],'transition':['self','state','joint_action'],'observation':['self','state','joint_action','next_state','player'],'reward':['self','state','joint_action','next_state','player'],'is_terminal':['self','state']}
def check_contract(source:str)->dict[str,Any]:
    out={'syntax_ok':False,'base_class_ok':False,'required_methods_ok':False,'signature_ok':False,'instantiation_ok':False,'errors':[]}
    try: tree=ast.parse(source); out['syntax_ok']=True
    except SyntaxError as e: out['errors']=[f'SyntaxError: {e}']; return out
    cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='GeneratedPOSG'),None)
    if not cls: out['errors'].append('missing class GeneratedPOSG'); return out
    out['base_class_ok']=any(isinstance(b,ast.Name) and b.id=='AbstractPOSG' for b in cls.bases)
    if not out['base_class_ok']: out['errors'].append('class must inherit AbstractPOSG')
    methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}; out['required_methods_ok']=set(REQUIRED)<=set(methods)
    for name,args in REQUIRED.items():
        if name not in methods: out['errors'].append(f'missing {name}()'); continue
        actual=[a.arg for a in methods[name].args.args]
        if actual!=args: out['errors'].append(f'{name} signature {actual} != {args}')
    out['signature_ok']=not any('signature' in e for e in out['errors'])
    out['instantiation_ok']=out['base_class_ok'] and out['required_methods_ok'] and out['signature_ok']
    return out
