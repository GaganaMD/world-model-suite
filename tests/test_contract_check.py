import unittest
from src.evaluation.contract_check import check_contract

VALID='''class GeneratedPOSG(AbstractPOSG):\n @property\n def players(self): return ["robot"]\n def initial_state(self): return "s0"\n def legal_actions(self,state,player): return ["a"]\n def transition(self,state,joint_action): return {"g":1.0}\n def observation(self,state,joint_action,next_state,player): return "x"\n def reward(self,state,joint_action,next_state,player): return 0.0\n def is_terminal(self,state): return state == "g"\n'''
class ContractCheckTests(unittest.TestCase):
 def test_valid(self): self.assertTrue(check_contract(VALID)['instantiation_ok'])
 def test_missing_and_signature(self):
  r=check_contract('class GeneratedPOSG(AbstractPOSG):\n def transition(self,state,action): return {}')
  self.assertFalse(r['required_methods_ok']); self.assertFalse(r['instantiation_ok'])
 def test_syntax(self): self.assertFalse(check_contract('not python !!!')['syntax_ok'])
