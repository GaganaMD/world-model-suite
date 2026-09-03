from tests.fixtures.physical_ai_generated.fixture_factory import source_for
from experiments.physical_ai_subset.final_study.evaluate_candidate import evaluate_python_code

SCENARIOS=['P1_BLOCKED_DOOR','P2_FRAGILE_DELIVERY','P3_BATTERY_DELIVERY','P4b_COLLISION_RISK_TRADEOFF','P5_IRREVERSIBLE_SWITCH']
def test_all_reference_equivalent_python_candidates():
    for sid in SCENARIOS:
        r=evaluate_python_code(sid,source_for(sid),model='fixture')
        assert r['contract_valid'] and r['feature_contract_valid'] and r['lane1_valid']
        assert r['structural_evaluable'] and r['planning_eligible']
        assert r['policy_agreement']==1.0 and r['planning_regret']==0.0
def test_p4b_wrong_python_candidate_is_valid_and_decision_relevant():
    r=evaluate_python_code('P4b_COLLISION_RISK_TRADEOFF',source_for('P4b_COLLISION_RISK_TRADEOFF',True),model='fixture')
    assert r['contract_valid'] and r['lane1_valid'] and r['planning_eligible']
