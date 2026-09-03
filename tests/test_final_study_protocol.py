import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/'experiments/physical_ai_subset/final_study'

def test_final_matrix_is_exactly_30_and_canonical():
    rows=list(csv.DictReader((ROOT/'candidate_matrix.csv').open()))
    assert len(rows)==30
    assert len({r['candidate_id'] for r in rows})==30
    assert {r['scenario'] for r in rows}=={'P1_BLOCKED_DOOR','P2_FRAGILE_DELIVERY','P3_BATTERY_DELIVERY','P4b_COLLISION_RISK_TRADEOFF','P5_IRREVERSIBLE_SWITCH'}

def test_prompt_and_reference_manifests_cover_matrix():
    p=json.loads((ROOT/'prompt_hashes.json').read_text())['hashes']
    r=json.loads((ROOT/'reference_identities.json').read_text())
    assert set(p)==set(r)
    assert 'P4b_COLLISION_RISK_TRADEOFF' in p
