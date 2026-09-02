import unittest
from src.evaluation.physical_features import validate_features, external_predicates

class PhysicalFeatureTests(unittest.TestCase):
    def test_valid_p4(self):
        f={'location':'route','goal_reached':False,'collision':False}
        self.assertEqual(validate_features('P4',f),[])
        self.assertEqual(external_predicates('P4',f),{'success':False,'unsafe':False,'failure':False})
    def test_missing_and_malformed(self):
        self.assertTrue(validate_features('P4',{'location':'bad','goal_reached':False}))
    def test_p4_accepts_scenario_defined_location_label(self):
        self.assertEqual(validate_features('P4',{'location':'safe_corridor','goal_reached':False,'collision':False}),[])
    def test_features_do_not_validate_dynamics(self):
        self.assertEqual(validate_features('P4',{'location':'route','goal_reached':False,'collision':False}),[])
