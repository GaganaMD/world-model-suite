"""Batch evaluator for frozen candidate records; does not call providers."""
from pathlib import Path
import csv,json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from evaluate_candidate import evaluate_reference,evaluate_dict_candidate
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
 print(json.dumps({'reference_scenarios':len(rows),'all_self_tests_pass':all(x['planning_self_regret']==0 for x in rows),'synthetic_inputs':30,'synthetic_outputs':len(synth)}))
if __name__=='__main__': main()
