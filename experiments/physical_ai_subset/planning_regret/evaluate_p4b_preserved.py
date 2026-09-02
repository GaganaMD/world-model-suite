"""Offline corrected evaluation of the three preserved P4b outputs."""
from pathlib import Path
import csv,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from experiments.run_hardened_openrouter_game_study import extract_python, static_contract_errors
from world_model_eda.python_posg import execute_generated_posg, rollout_world_model
from src.evaluation.pipeline import _load_model
from src.evaluation.lane1_mechanical import evaluate_mechanical
from src.evaluation.physical_features import check_instance_features
from json_generation.lane2 import lane2_score
from experiments.physical_ai_subset.planning_regret.p4b_reference import reference,identity
from src.evaluation.reference_identity import assert_reference_identity
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'experiments/physical_ai_subset/p4b_pilot'; OUT=BASE/'corrected_eval'; OUT.mkdir(parents=True,exist_ok=True)
def main():
 ref=reference(); assert_reference_identity(ref,scenario_id='P4b_COLLISION_RISK_TRADEOFF',reference_variant='p4b_v1',objective_id='p4b_tradeoff_v1'); (OUT/'reference_identity.json').write_text(json.dumps(identity(ref),indent=2))
 rows=[]
 for model in ('gpt_5_6_sol','claude_opus_5','llama_3_3_70b'):
  p=BASE/'parsed'/f'{model}_P4_r1.py'; code=p.read_text(); ex=execute_generated_posg(code); row={'scenario_id':'P4b_COLLISION_RISK_TRADEOFF','model':model,'provider_success':True,'contract_valid':not static_contract_errors(code),'feature_contract_valid':False,'lane1_valid':False,'planning_eligible':False,'planning_exclusion_reason':'','structural_f1':'NA','exact_structural_match':'NA','p_gen':'NA','reference_p':.5,'reference_optimal_action':'safe_route','generated_optimal_action':'NA','reference_optimal_value':.6,'generated_predicted_value':'NA','generated_policy_reference_value':'NA','planning_regret':'NA','policy_agreement':'NA','policy_mapping_coverage':'NA','reference_success_probability':'NA','transferred_success_probability':'NA','reference_unsafe_probability':0.0,'transferred_unsafe_probability':'NA','unsafe_probability_delta':'NA','manual_classification':'mechanical failure'}
  if ex['success']:
   inst=ex['world_model']; roll=rollout_world_model(inst,max_states=100,max_depth=10); row['lane1_valid']=not roll['errors'] and not roll['truncated']; states=list(roll['states']); fc=check_instance_features('P4',inst,states); row['feature_contract_valid']=fc['state_features_schema_valid'];
   if row['lane1_valid']:
    c=json.loads(__import__('world_model_eda.python_posg',fromlist=['canonical_rollout_json']).canonical_rollout_json(roll)); adapted=_load_model(c,'candidate'); s=lane2_score(ref,adapted,horizon=3,sa_iters=1000); row.update(structural_f1=s['lane2'],exact_structural_match=s['lane2']==1.0)
   if row['lane1_valid'] and row['feature_contract_valid'] and all(a in ('safe_route','risky_route') for st in states for a in getattr(inst,'legal_actions')(st,'robot')): row['planning_exclusion_reason']='policy transfer not yet implemented'; row['planning_eligible']=False
   else: row['planning_exclusion_reason']='feature contract or rollout failure'
  else: row['planning_exclusion_reason']='execution failure'
  if row['lane1_valid']: row['manual_classification']='mechanically valid but planning-ineligible'
  rows.append(row)
 with (OUT/'results.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
if __name__=='__main__': main()
