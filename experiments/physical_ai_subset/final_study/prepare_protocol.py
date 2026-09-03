"""Materialize deterministic references, prompts, identities, and matrix manifests."""
from pathlib import Path
import hashlib,json,csv
from reference_spec import canonical_specs
ROOT=Path(__file__).resolve().parent; PROMPTS=ROOT/'prompts'; REFS=ROOT/'references'; CONFIGS=ROOT/'configs'
MODEL_KEYS={'GPT':'openai/gpt-5.6-sol','Claude':'anthropic/claude-opus-5','Llama':'meta-llama/llama-3.3-70b-instruct'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for d in (PROMPTS,REFS,CONFIGS,ROOT/'raw',ROOT/'parsed',ROOT/'contract_checks',ROOT/'feature_checks',ROOT/'lane1',ROOT/'structural',ROOT/'planning',ROOT/'results',ROOT/'figures',ROOT/'case_studies'): d.mkdir(exist_ok=True)
 specs=canonical_specs(); (REFS/'references.json').write_text(json.dumps(specs,indent=2),encoding='utf-8')
 ids=[]; refs={}; ph={}
 scaffold=(ROOT.parent/'p4b_pilot'/'prompt.txt').read_text(encoding='utf-8')
 for s in specs:
  sid=s['scenario_id']; p=PROMPTS/f'{sid}.txt'; text=scaffold+'\n\nSCENARIO_ID: '+sid+'\nSCENARIO: '+s['objective']+'\nCANONICAL_ACTIONS: '+', '.join(s['allowed_actions'])+'\nREQUIRED_STATE_FEATURES: '+json.dumps(s['states'][0]['state_features'],sort_keys=True)+'\n'
  p.write_text(text,encoding='utf-8'); ph[sid]=sha(p)
  raw=json.dumps(s,sort_keys=True).encode(); refs[sid]={'scenario_id':sid,'reference_variant':s['reference_variant'],'objective_id':s['objective_id'],'reference_hash':hashlib.sha256(raw).hexdigest(),'reference_file':str((REFS/'references.json').relative_to(ROOT)),'planning_horizon':10,'feature_contract_version':'physical-features-v1'}
 for mkey,mid in MODEL_KEYS.items():
  for s in specs:
   for run in (1,2): ids.append({'candidate_id':f"{s['scenario_id']}_{mkey}_R{run}",'scenario':s['scenario_id'],'model':mid,'run':run,'prompt_hash':ph[s['scenario_id']]})
 (ROOT/'prompt_hashes.json').write_text(json.dumps({'protocol_version':'physical-ai-v1','hashes':ph},indent=2),encoding='utf-8')
 (ROOT/'reference_identities.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')
 with (ROOT/'candidate_matrix.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=ids[0]); w.writeheader(); w.writerows(ids)
 (ROOT/'configs'/'generation_config.json').write_text(json.dumps({'models':MODEL_KEYS,'runs':[1,2],'retries':0,'repairs':False,'protocol_version':'physical-ai-v1'},indent=2),encoding='utf-8')
if __name__=='__main__': main()
