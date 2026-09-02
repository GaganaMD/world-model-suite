import csv, subprocess, sys, unittest
from pathlib import Path
class P4bCalibrationTests(unittest.TestCase):
 def test_threshold_and_policy_flip(self):
  p=Path('experiments/physical_ai_subset/planning_regret/p4b_calibration.csv'); subprocess.run([sys.executable,'experiments/physical_ai_subset/planning_regret/run_p4b_calibration.py'],check=True)
  rows=list(csv.DictReader(p.open())); self.assertTrue(0<float(rows[0]['p_star'])<1); self.assertEqual(rows[1]['selected_action'],'risky_route'); self.assertEqual(rows[-1]['selected_action'],'safe_route'); self.assertGreater(float(rows[1]['planning_regret']),0)
 def test_old_calibration_preserved(self):
  rows=list(csv.DictReader(Path('experiments/physical_ai_subset/planning_regret/p4_risk_calibration.csv').open())); self.assertTrue(all(r['optimal_action']=='safe_route' for r in rows)); self.assertTrue(all(float(r['planning_regret'])==0 for r in rows))
