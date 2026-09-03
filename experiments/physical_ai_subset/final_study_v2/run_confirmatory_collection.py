"""Frozen v2 collection planner. Network dispatch is intentionally opt-in."""
from pathlib import Path
import csv,json,hashlib,argparse
ROOT=Path(__file__).resolve().parent
def plan():
 p=json.loads((ROOT/'protocol.json').read_text()); rows=list(csv.DictReader((ROOT/'candidate_matrix.csv').open()))
 out=[]; hashes=json.loads((ROOT/'prompt_hashes.json').read_text())['hashes']
 for r in rows:
  sid=r['scenario']; pp=ROOT/'rendered_prompts'/f'{sid}.txt'; assert pp.exists(); h=hashlib.sha256(pp.read_bytes()).hexdigest(); assert h==hashes[sid]
  out.append({'candidate_id':r['candidate_id'],'scenario_id':sid,'model_id':r['model'],'run_id':r['run'],'prompt_hash':h,'raw_path':str(ROOT/'confirmatory'/'raw'/f"{r['candidate_id']}.txt")})
 assert len(out)==30 and len({x['candidate_id'] for x in out})==30
 return out
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--dry-run',action='store_true'); args=ap.parse_args(); rows=plan(); print(json.dumps({'cells':len(rows),'unique_ids':len({r['candidate_id'] for r in rows}),'prompt_hashes_valid':len(rows),'network_calls':0,'legacy_writes':0,'rows':rows},indent=2))
if __name__=='__main__': main()
