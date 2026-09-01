import unittest
from src.planning.finite_horizon import finite_horizon_plan, evaluate_policy
from src.evaluation.reachability_metrics import reachable_states, reversible_edges


class NextExperimentTests(unittest.TestCase):
    def setUp(self):
        self.m = {'players':[{'id':'p'}], 'initial':[{'state':'s','p':1}], 'states':[
            {'id':'s','actions':[{'by':{'p':'go'},'next':[{'state':'g','p':1}]}]},
            {'id':'g','terminal':True,'reward':{'p':1}}]}
    def test_planner_and_evaluation(self):
        r=lambda s,a,n: 1.0 if n=='g' else 0.0
        p=finite_horizon_plan(self.m,'p',2,r)
        self.assertEqual(p['initial_value'],1.0)
        self.assertEqual(evaluate_policy(self.m,p['policy'],r,2),1.0)
    def test_reachability(self):
        self.assertEqual(reachable_states(self.m), {'s','g'})
        self.assertEqual(reversible_edges(self.m), set())

if __name__ == '__main__': unittest.main()
