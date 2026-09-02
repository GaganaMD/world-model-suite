"""Pre-registered, no-call decision-relevant P4b calibration."""
from pathlib import Path
import copy,csv,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.planning.finite_horizon import finite_horizon_plan
from json_generation.lane2 import lane2_score
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'experiments/physical_ai_subset/planning_regret'; OUT.mkdir(parents=True,exist_ok=True)
BASE=next(x for x in json.loads((ROOT/'experiments/paper_extension_results/physical_reference/references.json').read_text()) if x['id']=='P4_collision_risk')
SAFE_COST=.4; RISKY_COST=.1; COLLISION_PENALTY=0.35; REFERENCE_RISK=.5
PSTAR=((1-RISKY_COST)-(1-SAFE_COST))/((1-RISKY_COST)+(COLLISION_PENALTY+RISKY_COST))
def utility(model):
 def r(state,action,next_state):
  cost=SAFE_COST if action.get('robot')=='safe_route' else RISKY_COST
  terminal=next(s for s in model['states'] if s['id']==next_state).get('state_features',{})
  if terminal.get('goal_reached',False): return 1.0-cost
  if terminal.get('collision',False): return -COLLISION_PENALTY-cost
  return -cost
 return r
def main():
 rows=[]
 for p in (0,.1,.2,.22,PSTAR,.3,.5,1.0):
  m=copy.deepcopy(BASE); a=next(a for a in m['states'][0]['actions'] if a['by']['robot']=='risky_route'); a['next']=[{'state':'goal','p':1-p},{'state':'collision','p':p}]
  # External features are normalized for the hand-authored calibration.
  for s in m['states']:
   if s['id']=='goal': s['state_features']={'location':'goal','goal_reached':True,'collision':False}
   elif s['id']=='collision': s['state_features']={'location':'collision','goal_reached':False,'collision':True}
   else: s['state_features']={'location':'route','goal_reached':False,'collision':False}
  pl=finite_horizon_plan(m,'robot',10,utility(m)); act=pl['policy'][('s0',10)]['robot']; refv=.6 if act=='safe_route' else (1-RISKY_COST)*(1-REFERENCE_RISK)+(-COLLISION_PENALTY-RISKY_COST)*REFERENCE_RISK
  rows.append({'variant':'P4b_COLLISION_RISK_TRADEOFF','assumed_collision_probability':p,'structural_f1':lane2_score(BASE,m,horizon=3,sa_iters=500)['lane2'],'selected_action':act,'reference_action':'safe_route','model_predicted_value':pl['initial_value'],'reference_policy_value':refv,'planning_regret':.6-refv,'unsafe_probability_under_reference':REFERENCE_RISK if act=='risky_route' else 0.0,'p_star':PSTAR})
 with (OUT/'p4b_calibration.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
 print('p*',PSTAR)
if __name__=='__main__': main()
