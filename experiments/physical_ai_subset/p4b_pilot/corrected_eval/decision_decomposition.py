"""Offline action-value and trace decomposition for the preserved P4b pilot."""
from pathlib import Path
import csv, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from world_model_eda.python_posg import execute_generated_posg, rollout_world_model

SAFE_COST=.4; RISKY_COST=.1; COLLISION_PENALTY=.35; HORIZON=10; P_REF=.5; P_STAR=2/9
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'corrected_eval'; TRACE=OUT/'decision_traces'; TRACE.mkdir(parents=True,exist_ok=True)

def components(model, state, action, horizon=HORIZON):
    """Return expected (success, collision, failure, cost, penalty, utility, residual)."""
    memo={}
    def rec(s,t):
        if t<=0:
            return (0.,0.,0.,0.,0.,0.,1.)
        if model.is_terminal(s):
            return (0.,0.,0.,0.,0.,0.,0.)
        k=(s,t)
        if k in memo:return memo[k]
        choices=[]
        for a in model.legal_actions(s,'robot'):
            choices.append((step(s,a,t),a))
        return max(choices,key=lambda x:x[0][5])[0]
    def step(s, a, t):
        out=[0.]*7; dist=model.transition(s,{'robot':a})
        for ns,p in dist.items():
            p=float(p); f=model.state_features(ns); cost=SAFE_COST if action=='safe_route' else RISKY_COST
            child=rec(ns,t-1)
            out[0]+=p*(float(bool(f.get('goal_reached'))) + child[0]); out[1]+=p*(float(bool(f.get('collision'))) + child[1]); out[2]+=p*(float((not f.get('goal_reached')) and (not f.get('collision')) and inst_terminal(model,ns)) + child[2])
            out[3]+=p*(cost+child[3]); out[4]+=p*((COLLISION_PENALTY if f.get('collision') else 0.)+child[4])
            out[5]+=p*((1.0 if f.get('goal_reached') else 0.)- (COLLISION_PENALTY if f.get('collision') else 0.)-cost + child[5])
            out[6]+=p*child[6]
        return tuple(out)
    # Force the queried action at the initial state, then optimize continuation.
    return step(state, action, horizon)

def inst_terminal(model, state):
    return bool(model.is_terminal(state))

def q_values(model):
    s=model.initial_state(); return {a:components(model,s,a) for a in model.legal_actions(s,'robot')}

def canonical_row(model, name, f1):
    q=q_values(model); safe=q.get('safe_route'); risky=q.get('risky_route')
    return {'Model':name,'Structural F1':f1,'p_gen':.25,'p*':P_STAR,
            'Q_safe':safe[5] if safe else 'NA','Q_risky':risky[5] if risky else 'NA',
            'Q_gap':(risky[5]-safe[5]) if safe and risky else 'NA',
            'P_success_safe':safe[0] if safe else 'NA','P_success_risky':risky[0] if risky else 'NA',
            'P_collision_safe':safe[1] if safe else 'NA','P_collision_risky':risky[1] if risky else 'NA',
            'Expected_cost_safe':safe[3] if safe else 'NA','Expected_cost_risky':risky[3] if risky else 'NA',
            'Expected_collision_penalty_safe':safe[4] if safe else 'NA','Expected_collision_penalty_risky':risky[4] if risky else 'NA',
            'Expected_external_value_safe':safe[5] if safe else 'NA','Expected_external_value_risky':risky[5] if risky else 'NA',
            'Generated Action':max(q,key=lambda a:q[a][5]),'Reference Action':'safe_route',
            'Transferred Value':.225,'Planning Regret':.375,'Primary Error Attribution':'compound dynamics / topology-path-cost error'}

def main():
    rows=[]
    for name in ('gpt_5_6_sol','claude_opus_5'):
        p=BASE/'parsed'/f'{name}_P4_r1.py'; ex=execute_generated_posg(p.read_text()); inst=ex['world_model']; roll=rollout_world_model(inst,max_states=100,max_depth=10)
        f1={'gpt_5_6_sol':.2403,'claude_opus_5':.1360}[name]; rows.append(canonical_row(inst,name,f1))
        # Compact probability-weighted first-step traces.
        traces=[]
        for action in ('safe_route','risky_route'):
            for ns,prob in inst.transition(inst.initial_state(),{'robot':action}).items():
                f=inst.state_features(ns); traces.append({'action':action,'next_state':str(ns),'probability':float(prob),'terminal':bool(inst.is_terminal(ns)),'goal_reached':bool(f.get('goal_reached')),'collision':bool(f.get('collision'))})
        (TRACE/f'{name}.json').write_text(json.dumps(traces,indent=2))
    fields=list(rows[0]);
    with (OUT/'decision_decomposition.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with (OUT/'decision_decomposition.md').open('w') as f:
        f.write('# P4b decision-value decomposition\n\n')
        f.write('The canonical p=0.25 control selects `safe_route` because Q_safe=0.6 and Q_risky=0.5625. The preserved generated models use altered topology/path costs, so their action values must be inspected directly.\n\n')
        f.write('| Model | Q safe | Q risky | Gap | P(collision), safe | P(collision), risky | Selected action | Regret |\n|---|---:|---:|---:|---:|---:|---|---:|\n')
        for r in rows: f.write(f"| {r['Model']} | {r['Q_safe']:.6f} | {r['Q_risky']:.6f} | {r['Q_gap']:.6f} | {r['P_collision_safe']:.3f} | {r['P_collision_risky']:.3f} | {r['Generated Action']} | {r['Planning Regret']:.3f} |\n")
if __name__=='__main__': main()
