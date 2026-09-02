"""Run exactly six authorized P4 hosted generations and evaluate them."""
from __future__ import annotations
import argparse,csv,json,os,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from experiments.run_hardened_openrouter_game_study import extract_python, static_contract_errors, load_dotenv
from world_model_eda.python_posg import execute_generated_posg, rollout_world_model, canonical_rollout_json
from src.evaluation.lane1_mechanical import evaluate_mechanical
from src.evaluation.pipeline import _load_model
from json_generation.lane2 import lane2_score

MODELS={'gpt_5_6_sol':'openai/gpt-5.6-sol','claude_opus_5':'anthropic/claude-opus-5','llama_3_3_70b':'meta-llama/llama-3.3-70b-instruct'}
OUT=ROOT/'experiments/physical_ai_subset/p4b_pilot'; PROMPT=(ROOT/'data/Test_Cases/Physical/P4b_collision_risk_tradeoff_prompt.txt').read_text(encoding='utf-8')
REF=[x for x in json.loads((ROOT/'experiments/paper_extension_results/physical_reference/references.json').read_text()) if x['id']=='P4_collision_risk'][0]

def load_env(): load_dotenv(); key=os.getenv('OPENROUTER_API_KEY');
def call(model,prompt):
    body={'model':model,'messages':[{'role':'system','content':'Return only the requested Python class.'},{'role':'user','content':prompt}],'temperature':0,'max_tokens':12000,'reasoning':{'enabled':False}}
    r=requests.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY'],'Content-Type':'application/json'},json=body,timeout=120); r.raise_for_status(); b=r.json(); c=b['choices'][0].get('message',{}).get('content') or ''; return c,{'provider':b.get('provider'),'model_returned':b.get('model'),'finish_reason':b['choices'][0].get('finish_reason'),'id':b.get('id')}

def main():
    load_env();
    if not os.getenv('OPENROUTER_API_KEY'): raise SystemExit('OPENROUTER_API_KEY missing; no calls made')
    for sub in ('raw','parsed','validation','graphs','planning','manual_audit','figures'): (OUT/sub).mkdir(parents=True,exist_ok=True)
    rows=[]; summary=[]
    for slug,model in MODELS.items():
      for run in (1,):
        tag=f'{slug}_P4_r{run}'; meta={'scenario':'P4_collision_risk','model':model,'run':run,'timestamp':datetime.now(timezone.utc).isoformat(),'provider_status':'returned'}
        try:
          raw,callmeta=call(model,PROMPT); (OUT/'raw'/f'{tag}.txt').write_text(raw,encoding='utf-8'); meta.update(callmeta)
        except Exception as e:
          meta.update(provider_status='failed',error=f'{type(e).__name__}: {e}'); rows.append(meta); continue
        code,parse_error=extract_python(raw); (OUT/'parsed'/f'{tag}.py').write_text(code,encoding='utf-8'); meta.update(parse_success=parse_error is None,parse_error=parse_error or '')
        errors=static_contract_errors(code); meta['first_pass_lane1']=False
        if not errors:
          ex=execute_generated_posg(code)
          if ex.get('success'):
            roll=rollout_world_model(ex['world_model'],max_states=100,max_depth=10); meta['first_pass_lane1']=not bool(roll.get('errors')) and not roll.get('truncated');
            if meta['first_pass_lane1']:
              model_json=json.loads(canonical_rollout_json(roll)); (OUT/'graphs'/f'{tag}.json').write_text(json.dumps(model_json,indent=2),encoding='utf-8'); adapted=_load_model(model_json,'candidate'); meta['final_lane1']=evaluate_mechanical(adapted)['passed']
              try:
                sc=lane2_score(REF,adapted,horizon=3,sa_iters=1000); meta.update(structural_coverage=sc['coverage'],structural_precision=sc['precision'],structural_f1=sc['lane2'],exact_match=sc['lane2']==1.0)
              except Exception as e: meta['structural_error']=str(e)
            else: meta['validation_errors']=roll.get('errors',[])
          else: meta['validation_errors']=ex.get('errors',[])
        else: meta['validation_errors']=errors
        meta.update(strict_planning_eligible=False,planning_regret=None,policy_agreement=None,notes='Pilot records mechanical/structural outputs; external state predicates require explicit generated feature alignment.')
        rows.append(meta)
    fields=sorted({k for r in rows for k in r});
    with (OUT/'pilot_results.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    (OUT/'prompt.txt').write_text(PROMPT,encoding='utf-8'); (OUT/'config.json').write_text(json.dumps({'models':MODELS,'runs':[1,2],'calls_authorized':6},indent=2),encoding='utf-8')
if __name__=='__main__': main()
