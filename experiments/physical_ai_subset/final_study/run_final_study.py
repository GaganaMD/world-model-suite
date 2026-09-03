from pathlib import Path
import csv,json,os,hashlib,sys
from datetime import datetime,timezone
import requests
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT.parents[2]))
from experiments.run_hardened_openrouter_game_study import load_dotenv,extract_python,static_contract_errors
from world_model_eda.python_posg import execute_generated_posg,rollout_world_model
from src.evaluation.physical_features import check_instance_features

def main():
 load_dotenv(ROOT.parents[2]/'.env')
 matrix=list(csv.DictReader((ROOT/'candidate_matrix.csv').open())); hashes=json.loads((ROOT/'prompt_hashes.json').read_text())['hashes']; refs=json.loads((ROOT/'reference_identities.json').read_text())
 if len(matrix)!=30: raise SystemExit('matrix is not 30 cells')
 for d in ('raw','parsed','contract_checks','feature_checks','lane1','structural','planning','results'): (ROOT/d).mkdir(exist_ok=True)
 key=os.getenv('OPENROUTER_API_KEY')
 if not key: raise SystemExit('OPENROUTER_API_KEY missing; no calls made')
 rows=[]
 for x in matrix:
  sid=x['scenario']; cid=x['candidate_id']; pp=ROOT/'prompts'/f'{sid}.txt'; prompt=pp.read_text()
  if hashlib.sha256(pp.read_bytes()).hexdigest()!=hashes[sid]: raise SystemExit('prompt hash mismatch '+sid)
  req={'model':x['model'],'messages':[{'role':'system','content':'Return only the requested Python class.'},{'role':'user','content':prompt}],'temperature':0,'max_tokens':12000,'reasoning':{'enabled':False}}
  row={'candidate_id':cid,'scenario':sid,'model':x['model'],'run':x['run'],'provider_success':False,'contract_valid':False,'feature_contract_valid':False,'lane1_valid':False,'planning_eligible':False,'planning_exclusion_reason':'provider failure','structural_f1':'NA','exact_structural_match':'NA','reference_optimal_action':'safe_route' if sid.startswith('P4b') else 'NA','generated_optimal_action':'NA','policy_agreement':'NA','policy_mapping_coverage':'NA','reference_optimal_value':0.6 if sid.startswith('P4b') else 1.0,'generated_predicted_value':'NA','transferred_reference_value':'NA','planning_regret':'NA','success_probability_reference':'NA','success_probability_transferred':'NA','success_delta':'NA','unsafe_probability_reference':'NA','unsafe_probability_transferred':'NA','unsafe_delta':'NA','p_gen':'NA','p_ref':0.5 if sid.startswith('P4b') else 'NA','risk_absolute_error':'NA','Q_safe':'NA','Q_risky':'NA','Q_gap':'NA','error_attribution':'provider failure','notes':'','prompt_hash':hashes[sid],'reference_variant':refs[sid]['reference_variant'],'objective_id':refs[sid]['objective_id'],'timestamp':datetime.now(timezone.utc).isoformat()}
  try:
   r=requests.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=req,timeout=180); r.raise_for_status(); b=r.json(); raw=b['choices'][0].get('message',{}).get('content') or ''; row.update(provider_success=True,provider=b.get('provider'),model_returned=b.get('model'),finish_reason=b['choices'][0].get('finish_reason'),request_id=b.get('id'))
  except Exception as e: raw=''; row['notes']=f'{type(e).__name__}: {e}'
  (ROOT/'raw'/f'{cid}.txt').write_text(raw); (ROOT/'configs'/f'{cid}.json').write_text(json.dumps(req,indent=2))
  if raw:
   code,err=extract_python(raw); (ROOT/'parsed'/f'{cid}.py').write_text(code); row['contract_valid']=not bool(static_contract_errors(code))
   ex=execute_generated_posg(code)
   if ex.get('success'):
    inst=ex['world_model']; roll=rollout_world_model(inst,max_states=200,max_depth=10); row['lane1_valid']=not bool(roll.get('errors')) and not roll.get('truncated'); states=list(roll.get('states',[])); case='P4' if sid.startswith('P4b') else sid.split('_')[0];
    try: row['feature_contract_valid']=check_instance_features(case,inst,states)['state_features_schema_valid']
    except Exception as e: row['notes']+=' feature:'+str(e)
    if row['lane1_valid'] and row['feature_contract_valid']: row['planning_eligible']=True; row['planning_exclusion_reason']='NA'
    elif row['lane1_valid']: row['planning_exclusion_reason']='feature contract failure'
   else: row['planning_exclusion_reason']='execution failure'
   if not row['lane1_valid']: row['error_attribution']='mechanical/interface failure'
  rows.append(row)
 fields=list(rows[0]);
 with (ROOT/'results'/'final_results.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
 (ROOT/'results'/'integrity_report.json').write_text(json.dumps({'attempted':len(rows),'unique_candidate_ids':len({r['candidate_id'] for r in rows}),'unauthorized_retries':0,'pilot_rows':0},indent=2))
 print('completed',len(rows),'authorized calls')
if __name__=='__main__': main()
