from pathlib import Path
import csv,json,hashlib
ROOT=Path(__file__).resolve().parent
REQ={'loading','contract','features','lane1','rollout','structural_adapter','structural_matcher','alignment','planning','transfer','reference_execution','regret','success','safety','p4b','batch','protocol','prompts','references','preflight'}
def validate_manifest(m):
 assert m.get('files'); cats={e.get('category') for e in m['files']}; assert REQ.issubset(cats)
 seen=set()
 for e in m['files']:
  key=(e.get('path'),e.get('category')); assert key not in seen; seen.add(key)
  q=(ROOT.parent.parent.parent/e['path']).resolve(); assert q.exists(); assert hashlib.sha256(q.read_bytes()).hexdigest()==e['sha256']
 return True
def main():
 p=json.loads((ROOT/'protocol.json').read_text()); rows=list(csv.DictReader((ROOT/'candidate_matrix.csv').open()))
 assert len(p['scenarios'])==5 and len(p['models'])==3 and p['runs']==[1,2] and p['total_calls']==30
 assert len(rows)==30 and len({r['candidate_id'] for r in rows})==30
 assert not any((ROOT/'raw').glob('*')) if (ROOT/'raw').exists() else True
 # Scenario-specific decision-error requirements are frozen: P4b is the
 # only required positive-regret control; P2/P5 have forced initial actions.
 assert set(p['scenarios'])=={'P1_BLOCKED_DOOR','P2_FRAGILE_DELIVERY','P3_BATTERY_DELIVERY','P4b_COLLISION_RISK_TRADEOFF','P5_IRREVERSIBLE_SWITCH'}
 mf=ROOT/'evaluator_manifest.json'; m=json.loads(mf.read_text()); validate_manifest(m)
 sv=ROOT/'structural_validation.csv'; assert sv.exists(); sr=list(csv.DictReader(sv.open())); assert len(sr)==5 and all(x['matcher_success']=='True' and x['structural_f1']!='NA' for x in sr)
 gp=ROOT/'generated_python_dry_run'/'integrity_report.json'; gi=json.loads(gp.read_text()); assert gi['inputs']==30 and gi['outputs']==30 and gi.get('failures',0)==0
 print('V2 PREFLIGHT PASS: 5 scenarios, 3 models, 2 runs, 30 cells, zero outputs')
if __name__=='__main__': main()
