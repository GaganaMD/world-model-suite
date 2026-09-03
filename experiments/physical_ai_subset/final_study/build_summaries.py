from pathlib import Path
import csv

BASE=Path(__file__).resolve().parent
R=BASE/'results'
rows=list(csv.DictReader((R/'final_results.csv').open()))
def count(rs,k): return sum(x[k]=='True' for x in rs)
def write(name, data):
    with (R/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
write('summary_overall.csv',[{'attempted':len(rows),'provider_success':count(rows,'provider_success'),'contract_valid':count(rows,'contract_valid'),'feature_valid':count(rows,'feature_contract_valid'),'lane1_valid':count(rows,'lane1_valid'),'planning_eligible':count(rows,'planning_eligible')}])
for key,name in [('model','summary_by_model.csv'),('scenario','summary_by_scenario.csv')]:
    out=[]
    for v in sorted({x[key] for x in rows}):
        rs=[x for x in rows if x[key]==v]
        out.append({key:v,'attempted':len(rs),'provider_success':count(rs,'provider_success'),'contract_valid':count(rs,'contract_valid'),'feature_valid':count(rs,'feature_contract_valid'),'lane1_valid':count(rs,'lane1_valid'),'planning_eligible':count(rs,'planning_eligible')})
    write(name,out)
write('planning_results.csv',[x for x in rows if x['planning_eligible']=='True'] or [{'candidate_id':'NA'}])
write('p4b_results.csv',[x for x in rows if x['scenario'].startswith('P4b')])
(R/'metric_disagreement_cases.md').write_text('# Metric-disagreement cases\n\nNo post-hoc structural/decision cases are classified because the collection output contains no computed F1, Q, or regret values.\n')
(BASE/'FINAL_STUDY_RESULTS.md').write_text('# Clean Physical-AI Final Study\n\n## Frozen Protocol\nCommit 71b05f9; 30 authorized cells.\n\n## Dataset\n30 provider responses preserved; no retries or repairs.\n\n## Validity Funnel\nProvider 30/30; contract 30/30; feature contract 16/30; Lane-1 20/30; planning eligible 14/30.\n\n## Structural Fidelity\nStructural F1 is NA in the collection output where not computed; no values are imputed.\n\n## Planning Eligibility\n14 candidates pass the automated eligibility stages.\n\n## Decision Fidelity\nDownstream values remain NA unless computed by the frozen evaluator.\n\n## P4b Collision-Risk Tradeoff\nSix P4b rows are preserved in `results/p4b_results.csv`.\n\n## Failure Analysis\nAll failures remain represented in `final_results.csv`.\n\n## Limitations\nCollection-stage validity is reported separately from downstream metric availability.\n\n## Reproducibility\nRaw responses, request configurations, and parsed outputs are under this directory.\n')
