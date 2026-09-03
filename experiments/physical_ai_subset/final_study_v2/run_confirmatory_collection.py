"""One-shot frozen v2 OpenRouter collection runner; imports never dispatch."""
from pathlib import Path
import csv,json,hashlib,argparse,os
from datetime import datetime,timezone
import requests
ROOT=Path(__file__).resolve().parent
def plan():
 rows=list(csv.DictReader((ROOT/'candidate_matrix.csv').open())); hashes=json.loads((ROOT/'prompt_hashes.json').read_text())['hashes']; out=[]
 for r in rows:
  sid=r['scenario']; data=(ROOT/'rendered_prompts'/f'{sid}.txt').read_bytes(); text=data.decode(); h=hashlib.sha256(data).hexdigest(); assert h==hashes[sid]
  out.append({'candidate_id':r['candidate_id'],'scenario_id':sid,'model_id':r['model'],'run_id':r['run'],'prompt_hash':h,'prompt':text})
 assert len(out)==30 and len({x['candidate_id'] for x in out})==30
 return out
def collect(transport,key,output_root,cells=None,execution_id=None):
 """Exactly one injectable transport invocation per cell; no retry loop."""
 if not execution_id: raise RuntimeError('explicit execution_id required')
 cells=plan() if cells is None else cells; base=(ROOT/'confirmatory').resolve(); root=(base/execution_id).resolve(); assert root.is_relative_to(base) and root!=base
 raw=root/'raw'; meta=root/'metadata'; integ=root/'integrity'
 if any(raw.glob('*')) if raw.exists() else False: raise RuntimeError('preexisting confirmatory artifacts')
 raw.mkdir(parents=True,exist_ok=True); meta.mkdir(parents=True,exist_ok=True); integ.mkdir(parents=True,exist_ok=True); records=[]
 for c in cells:
  rec={k:c[k] for k in ('candidate_id','scenario_id','model_id','run_id','prompt_hash')}; rec.update(execution_id=execution_id,attempt_number=1,timestamp=datetime.now(timezone.utc).isoformat(),provider_success=False)
  payload={'model':c['model_id'],'messages':[{'role':'user','content':c['prompt']}],'temperature':0,'max_tokens':12000}
  try:
   response=transport(payload,key); text=response['text']; p=raw/f"{c['candidate_id']}.txt"; p.write_text(text); rec.update(provider_success=True,raw_response_path=str(p),raw_sha256=hashlib.sha256(text.encode()).hexdigest(),provider_model=response.get('model'))
  except Exception as exc: rec.update(error_class=type(exc).__name__,error_message=str(exc))
  (meta/f"{c['candidate_id']}.json").write_text(json.dumps(rec,indent=2)); records.append(rec)
 (integ/'raw_responses.json').write_text(json.dumps(records,indent=2))
 completion={'execution_id':execution_id,'authorized_cells':len(cells),'recorded_outcomes':len(records),'unique_candidate_ids':len({r['candidate_id'] for r in records}),'provider_successes':sum(r['provider_success'] for r in records),'provider_failures':sum(not r['provider_success'] for r in records),'retries':0,'replacements':0,'fallbacks':0,'collection_complete':len(records)==len(cells),'completion_timestamp':datetime.now(timezone.utc).isoformat()}
 (integ/'completion.json').write_text(json.dumps(completion,indent=2)); return records
def openrouter_transport(payload,key):
 r=requests.post('https://openrouter.ai/api/v1/chat/completions',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=payload,timeout=180); r.raise_for_status(); b=r.json(); return {'text':b['choices'][0]['message']['content'],'model':b.get('model')}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--execute',action='store_true'); ap.add_argument('--execution-id'); args=ap.parse_args(); cells=plan()
 if not args.execution_id: raise SystemExit('--execution-id is required')
 if not args.execute: print(json.dumps({'cells':len(cells),'unique_ids':len({r['candidate_id'] for r in cells}),'prompt_hashes_valid':len(cells),'network_calls':0,'legacy_writes':0,'execution_id':args.execution_id},indent=2)); return
 if not os.getenv('OPENROUTER_API_KEY'):
  env=ROOT.parents[3]/'.env'
  if env.exists():
   for line in env.read_text().splitlines():
    if line.startswith('OPENROUTER_API_KEY='): os.environ['OPENROUTER_API_KEY']=line.split('=',1)[1].strip().strip('"').strip("'")
 key=os.getenv('OPENROUTER_API_KEY')
 if not key: raise SystemExit('OPENROUTER_API_KEY missing; zero requests dispatched')
 records=collect(openrouter_transport,key,ROOT/'confirmatory',cells,args.execution_id); print(json.dumps({'attempted':len(records),'successes':sum(r['provider_success'] for r in records)},indent=2))
if __name__=='__main__': main()
