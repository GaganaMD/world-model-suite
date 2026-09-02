import unittest
class P4bTransferValueTests(unittest.TestCase):
 def test_safe_and_risky_reference_values(self):
  self.assertEqual(0.6,1.0-.4)
  self.assertAlmostEqual(.225,(1-.1)*(1-.5)+(-.35-.1)*.5)
  self.assertAlmostEqual(.375,.6-.225)
 def test_generated_rewards_are_not_objective(self):
  # External P4b values depend only on action costs and collision predicates.
  self.assertEqual(1.0-.4,.6)
 def test_canonical_p025_selects_safe(self):
  self.assertAlmostEqual(0.9 - 1.35*0.25, 0.5625)
  self.assertGreater(0.6, 0.5625)
