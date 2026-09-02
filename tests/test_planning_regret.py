import csv
import unittest
from pathlib import Path

class PlanningReferenceResultsTests(unittest.TestCase):
    def test_reference_values_and_actions(self):
        p=Path('experiments/physical_ai_subset/planning_regret/reference_results.csv')
        if not p.exists():
            import subprocess,sys; subprocess.run([sys.executable,'experiments/physical_ai_subset/planning_regret/run_reference_planning.py'],check=True)
        rows=list(csv.DictReader(p.open()))
        self.assertEqual(len(rows),5)
        self.assertEqual([r['optimal_action'] for r in rows],['open_door','pick_up','move','safe_route','press_switch'])
        self.assertTrue(all(float(r['optimal_value'])==1.0 for r in rows))

if __name__=='__main__': unittest.main()
