"""No-call reference planning and P4 risk calibration."""
from pathlib import Path
import csv, json, math, copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.planning.finite_horizon import finite_horizon_plan, evaluate_policy
from src.evaluation.physical_features import external_predicates

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'experiments/physical_ai_subset/planning_regret'; OUT.mkdir(parents=True,exist_ok=True)
CASES=json.loads((ROOT/'experiments/paper_extension_results/physical_reference/references.json').read_text())
def feature_map(m):
 out={}
 for s in m['states']:
  f=dict(s.get('state_features',{})); sid=s['id']; case=m['id'].split('_')[0]
  if case=='P4': f.setdefault('location','collision' if 'collision' in sid else ('goal' if sid=='goal' else 'route')); f.setdefault('goal_reached',sid=='goal'); f.setdefault('collision',sid=='collision')
  elif case=='P1': f.setdefault('location','goal' if sid=='goal' else sid); f.setdefault('door_open',sid=='s1'); f.setdefault('goal_reached',sid=='goal')
  elif case=='P2': f.setdefault('robot_location',sid); f.setdefault('object_location',sid); f.setdefault('carrying',sid=='carrying'); f.setdefault('broken',sid=='broken'); f.setdefault('delivered',sid=='goal')
  elif case=='P3': f.setdefault('location',sid); f.setdefault('battery',1); f.setdefault('package_delivered',sid=='goal'); f.setdefault('failed',sid=='dead')
  else: f.setdefault('location',sid); f.setdefault('switch_pressed',sid=='s1'); f.setdefault('access_open',sid=='s1'); f.setdefault('goal_reached',sid=='goal')
  out[sid]=f
 return out
def objective(m, case):
    fm=feature_map(m)
    def reward(s,a,n):
        p=external_predicates(case,fm[n])
        return 1.0 if p['success'] else (-1.0 if p['failure'] else 0.0)
    return reward
def main():
 rows=[]
 for m in CASES:
  case=m['id'].split('_')[0]; plan=finite_horizon_plan(m,'robot',horizon=10,reward=objective(m,case)); action=plan['policy'].get(('s0',10),{}).get('robot','NA')
  rows.append({'scenario':m['id'],'initial_state':'s0','optimal_action':action,'optimal_value':plan['initial_value'],'success_probability':'reference objective','failure_probability':'reference objective','unsafe_probability':'reference objective'})
 with (OUT/'reference_results.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
 # P4 risk variants; canonical objective is success probability (terminal success=1, failure=0).
 p4=next(x for x in CASES if x['id']=='P4_collision_risk'); cal=[]
 for risk in (0.0,0.2,0.5,0.8,1.0):
  v=copy.deepcopy(p4); acts=v['states'][0]['actions']; risky=next(a for a in acts if a['by']['robot']=='risky_route'); risky['next']=[{'state':'goal','p':1-risk},{'state':'collision','p':risk}]
  rew=lambda s,a,n: 1.0 if n=='goal' else 0.0
  pl=finite_horizon_plan(v,'robot',10,rew); selected=pl['policy'][('s0',10)]['robot']; refv=1.0 if selected=='safe_route' else 1-risk
  cal.append({'assumed_collision_probability':risk,'optimal_action':selected,'model_value':pl['initial_value'],'reference_policy_value':refv,'planning_regret':1-refv,'collision_probability_under_selected_policy':risk if selected=='risky_route' else 0.0,'decision_threshold':'0.0 (success-probability objective)'})
 with (OUT/'p4_risk_calibration.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=cal[0]); w.writeheader(); w.writerows(cal)
if __name__=='__main__': main()
