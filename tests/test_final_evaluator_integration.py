import csv
from pathlib import Path

def test_synthetic_batch_has_thirty_rows():
    p=Path('experiments/physical_ai_subset/final_study/synthetic_dry_run/synthetic_results.csv')
    rows=list(csv.DictReader(p.open()))
    assert len(rows)==30
    assert len({r['candidate_id'] for r in rows})==30
    assert {r['scenario'] for r in rows}=={'P1_BLOCKED_DOOR','P2_FRAGILE_DELIVERY','P3_BATTERY_DELIVERY','P4b_COLLISION_RISK_TRADEOFF','P5_IRREVERSIBLE_SWITCH'}
    assert all(r['planning_eligible']=='True' for r in rows)
