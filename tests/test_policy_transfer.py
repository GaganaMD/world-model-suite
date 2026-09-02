import unittest
from src.evaluation.policy_transfer import transfer_initial_action
class M:
 def initial_state(self): return 'origin'
 def is_terminal(self,s): return False
 def legal_actions(self,s,p): return ['safe_route','risky_route']
class PolicyTransferTests(unittest.TestCase):
 def test_initial_context_ignores_location_name(self): self.assertEqual(transfer_initial_action(M())[0],'origin')
 def test_noncanonical_action_fails(self):
  class X(M):
   def legal_actions(self,s,p): return ['safe','risky']
  with self.assertRaises(ValueError): transfer_initial_action(X())
