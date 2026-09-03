"""Batch evaluator for frozen candidate records; does not call providers."""
from pathlib import Path
import csv,json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from evaluate_candidate import evaluate_reference
ROOT=Path(__file__).resolve().parent
def main():
 sids=json.loads((ROOT/'protocol.json').read_text())['scenarios']; rows=[evaluate_reference(s) for s in sids]
 out=ROOT/'reference_self_tests.csv'
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 print(json.dumps({'reference_scenarios':len(rows),'all_self_tests_pass':all(x['planning_self_regret']==0 for x in rows)}))
if __name__=='__main__': main()
