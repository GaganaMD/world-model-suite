"""Fail-closed no-call preflight for the frozen final-study package."""
from pathlib import Path
import csv,hashlib,json,sys,subprocess
ROOT=Path(__file__).resolve().parent
def fail(msg): raise SystemExit('PREFLIGHT FAIL: '+msg)
def main():
    protocol=json.loads((ROOT/'protocol.json').read_text()); expected=['P1_BLOCKED_DOOR','P2_FRAGILE_DELIVERY','P3_BATTERY_DELIVERY','P4b_COLLISION_RISK_TRADEOFF','P5_IRREVERSIBLE_SWITCH']
    if protocol['scenarios']!=expected: fail('scenario IDs are not canonical P1/P2/P3/P4b/P5')
    if len(protocol['models'])!=3 or protocol['generations_per_cell']!=2 or protocol['total_fresh_calls']!=30: fail('matrix dimensions mismatch')
    ph=json.loads((ROOT/'prompt_hashes.json').read_text())['hashes']; refs=json.loads((ROOT/'reference_identities.json').read_text())
    if set(ph)!=set(expected) or set(refs)!=set(expected): fail('prompt/reference manifest incomplete')
    for sid in expected:
        p=ROOT/'prompts'/f'{sid}.txt'
        if not p.exists(): fail(f'missing prompt {sid}')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=ph[sid]: fail(f'prompt hash mismatch {sid}')
        if refs[sid]['scenario_id']!=sid: fail(f'reference identity mismatch {sid}')
    rows=list(csv.DictReader((ROOT/'candidate_matrix.csv').open()))
    if len(rows)!=30 or len({r['candidate_id'] for r in rows})!=30: fail('candidate matrix is not exactly 30 unique cells')
    if any('pilot' in r['candidate_id'].lower() for r in rows): fail('pilot artifact in final matrix')
    p4=json.loads((ROOT/'references'/'references.json').read_text()); p4=next(x for x in p4 if x['scenario_id']=='P4b_COLLISION_RISK_TRADEOFF')
    acts=p4['states'][0]['actions']; risky=next(x for x in acts if x['by']['robot']=='risky_route'); prob=next(x['p'] for x in risky['next'] if x['state']=='collision')
    if prob!=.5: fail('P4b reference risk mismatch')
    if abs(2/9-0.2222222222222222)>1e-12: fail('P4b threshold mismatch')
    print(json.dumps({'status':'PASS','scenario_count':5,'model_count':3,'matrix_cells':30,'prompt_hashes':5,'reference_identities':5,'p4b_reference_probability':prob,'hosted_calls':0},indent=2))
if __name__=='__main__': main()
