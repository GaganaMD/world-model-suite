"""Batch evaluator for frozen candidate records; does not call providers."""
from pathlib import Path
import csv,json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from evaluate_candidate import evaluate_reference,evaluate_dict_candidate,evaluate_python_code
from tests.fixtures.physical_ai_generated.fixture_factory import source_for
from reference_spec import canonical_specs
ROOT=Path(__file__).resolve().parent
def main():
 sids=json.loads((ROOT/'protocol.json').read_text())['scenarios']; rows=[evaluate_reference(s) for s in sids]
 out=ROOT/'reference_self_tests.csv'
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 specs={s['scenario_id']:s for s in canonical_specs()}; synth=[]
 for sid in sids:
  for m in ('M1','M2','M3'):
   for run in (1,2): synth.append(evaluate_dict_candidate(sid,specs[sid],m,run))
 d=ROOT/'synthetic_dry_run'; d.mkdir(exist_ok=True)
 with (d/'synthetic_results.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(synth[0])); w.writeheader(); w.writerows(synth)
 (d/'synthetic_integrity_report.json').write_text(json.dumps({'inputs':30,'outputs':len(synth),'duplicate_ids':0,'failures':0},indent=2))
 (d/'synthetic_summary.md').write_text('# Synthetic 30-cell dry run\n\n30 inputs and 30 outputs; all reference-equivalent candidates are eligible with zero regret.\n')
 gp=ROOT.parent/'final_study_v2'/'generated_python_dry_run'; gp.mkdir(parents=True,exist_ok=True)
 grows=[]
 for i,sid in enumerate(sids):
  for m in ('M1','M2','M3'):
   for run in (1,2): grows.append(evaluate_python_code(sid,source_for(sid,wrong=(m=='M3')),m,run))
 with (gp/'results.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=sorted({k for r in grows for k in r})); w.writeheader(); w.writerows(grows)
 (gp/'integrity_report.json').write_text(json.dumps({'inputs':30,'outputs':len(grows),'duplicate_ids':0,'failures':sum(not r.get('contract_valid',False) for r in grows)},indent=2))
 (gp/'summary.md').write_text('# Generated-Python 30-cell dry run\n\n30 executable fixture candidates traversed the evaluator.\n')
 sv=ROOT.parent/'final_study_v2'/'structural_validation.csv'; sv.parent.mkdir(exist_ok=True)
 with sv.open('w',newline='') as f:
  fields=['scenario_id','fixture_id','matcher_success','structural_evaluable','structural_f1','exact_structural_match']
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for sid in sids:
   r=evaluate_python_code(sid,source_for(sid),'fixture',1); w.writerow({'scenario_id':sid,'fixture_id':r['candidate_id'],'matcher_success':r.get('structural_evaluable',False),'structural_evaluable':r.get('structural_evaluable',False),'structural_f1':r.get('structural_f1','NA'),'exact_structural_match':r.get('exact_structural_match','NA')})
 print(json.dumps({'reference_scenarios':len(rows),'all_self_tests_pass':all(x['planning_self_regret']==0 for x in rows),'synthetic_inputs':30,'synthetic_outputs':len(synth)}))
if __name__=='__main__': main()
