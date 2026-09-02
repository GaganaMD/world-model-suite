"""No-call calibration study: known structural errors and planning consequences."""
from __future__ import annotations
import csv, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.planning.finite_horizon import finite_horizon_plan, evaluate_policy
from src.evaluation.reachability_metrics import reachable_states, reversible_edges

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments'/'paper_extension_results'/'controlled_perturbations'

def fixture():
    return {'players':[{'id':'robot'}], 'initial':[{'state':'start','p':1.0}], 'states':[
      {'id':'start','terminal':False,'actions':[{'by':{'robot':'safe'},'next':[{'state':'goal','p':1.0}]},{'by':{'robot':'risky'},'next':[{'state':'unsafe','p':1.0}]}]},
      {'id':'goal','terminal':True,'reward':{'robot':1.0}}, {'id':'unsafe','terminal':True,'reward':{'robot':-1.0}}]}

def perturbations(ref):
    out={'reference':ref}
    miss=json.loads(json.dumps(ref)); miss['states'][0]['actions']=miss['states'][0]['actions'][:1]; out['remove_risky_action']=miss
    extra=json.loads(json.dumps(ref)); extra['states'][0]['actions'].append({'by':{'robot':'invented'},'next':[{'state':'goal','p':1.0}]}); out['add_action']=extra
    terminal=json.loads(json.dumps(ref)); terminal['states'][0]['terminal']=True; terminal['states'][0]['actions']=[]; out['premature_terminal']=terminal
    reverse=json.loads(json.dumps(ref)); reverse['states'][1]={'id':'goal','terminal':False,'actions':[{'by':{'robot':'return'},'next':[{'state':'start','p':1.0}]}]}; out['spurious_reverse_edge']=reverse
    return out

def main():
    OUT.mkdir(parents=True,exist_ok=True); ref=fixture(); rows=[]
    def r(s,a,ns): return float(next(x for x in ref['states'] if x['id']==ns).get('reward',{}).get('robot',0))
    base=finite_horizon_plan(ref,'robot',horizon=2,reward=r)
    for name,m in perturbations(ref).items():
        plan=finite_horizon_plan(m,'robot',horizon=2,reward=r)
        rows.append({'variant':name,'reference_value':base['initial_value'],'perturbed_value':plan['initial_value'],
                     'planning_regret':base['initial_value']-plan['initial_value'],
                     'reference_reachable':len(reachable_states(ref)),'variant_reachable':len(reachable_states(m)),
                     'reference_reversible_edges':len(reversible_edges(ref)),'variant_reversible_edges':len(reversible_edges(m)),
                     'selected_action':str(plan['policy'].get(('start',2),{}))})
    with (OUT/'results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    (OUT/'README.md').write_text('# Controlled structural perturbations\n\nHand-authored calibration POSG; no LLM calls. Rewards and perturbations are explicit.\n',encoding='utf-8')
if __name__=='__main__': main()
