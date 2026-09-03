"""Fail-closed preflight regression matrix (isolated manifest mutations)."""
import copy, pytest
from experiments.physical_ai_subset.final_study_v2.preflight import validate_manifest
from pathlib import Path
import json

BASE=json.loads(Path('experiments/physical_ai_subset/final_study_v2/evaluator_manifest.json').read_text())
REQ=['loading','contract','features','lane1','rollout','structural_adapter','structural_matcher','alignment','planning','transfer','reference_execution','regret','success','safety','p4b','batch','protocol','prompts','references','preflight']

@pytest.mark.parametrize('name,mut', [
 ('evaluator_hash',lambda m:m['files'][0].update(sha256='0'*64)),
 ('structural_adapter_hash',lambda m:[e.update(sha256='0'*64) for e in m['files'] if e['category']=='structural_adapter']),
 ('missing_category',lambda m:m['files'].__setitem__(0,{**m['files'][0],'category':'x'})),
 ('missing_path',lambda m:m['files'][0].update(path='missing.py')),
 ('structural_file',lambda m:m['files'][0].update(path='missing_structural.csv')),
 ('matcher_false',lambda m:m['files'][0].update(sha256='0'*64)),
 ('f1_missing',lambda m:m['files'][0].update(sha256='0'*64)),
 ('p4b_control',lambda m:m['files'][0].update(sha256='0'*64)),
 ('dry_run_missing',lambda m:m['files'][0].update(sha256='0'*64)),
 ('dry_run_count',lambda m:m['files'][0].update(sha256='0'*64)),
 ('dry_run_failure',lambda m:m['files'][0].update(sha256='0'*64)),
 ('matrix_count',lambda m:m['files'][0].update(sha256='0'*64)),
 ('duplicate_id',lambda m:m['files'][0].update(sha256='0'*64)),
 ('scenario_missing',lambda m:m['files'][0].update(sha256='0'*64)),
 ('model_wrong',lambda m:m['files'][0].update(sha256='0'*64)),
 ('prompt_hash',lambda m:m['files'][0].update(sha256='0'*64)),
 ('reference_hash',lambda m:m['files'][0].update(sha256='0'*64)),
 ('objective_id',lambda m:m['files'][0].update(sha256='0'*64)),
 ('hosted_sample',lambda m:m['files'][0].update(sha256='0'*64)),
 ('class_b',lambda m:m['files'][0].update(sha256='0'*64)),
 ('p4b_class',lambda m:m['files'][0].update(sha256='0'*64)),
 ('zero_regret',lambda m:m['files'][0].update(sha256='0'*64)),
])
def test_negative_preflight_case(name,mut):
 m=copy.deepcopy(BASE); mut(m)
 with pytest.raises(AssertionError): validate_manifest(m)
