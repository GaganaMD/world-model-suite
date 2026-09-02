import unittest
from src.evaluation.reference_identity import assert_reference_identity
class ReferenceIdentityTests(unittest.TestCase):
 def test_guard_accepts_p4b_and_rejects_legacy(self):
  r={'scenario_id':'P4b_COLLISION_RISK_TRADEOFF','reference_variant':'p4b_v1','objective_id':'p4b_tradeoff_v1'}
  self.assertTrue(assert_reference_identity(r,scenario_id='P4b_COLLISION_RISK_TRADEOFF',reference_variant='p4b_v1',objective_id='p4b_tradeoff_v1'))
  with self.assertRaises(ValueError): assert_reference_identity({'scenario_id':'P4'},scenario_id='P4b_COLLISION_RISK_TRADEOFF',reference_variant='p4b_v1',objective_id='p4b_tradeoff_v1')
