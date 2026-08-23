import unittest

from world_model_eda import AbstractPOSG, run_posg_experiment, validate_posg


RPS_SOURCE = '''
class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return {"start": 1.0}

    def legal_actions(self, state, player):
        return [] if self.is_terminal(state) else ["rock", "paper", "scissors"]

    def transition(self, state, joint_action):
        first, second = joint_action["player_1"], joint_action["player_2"]
        if first == second:
            return {"draw": 1.0}
        wins = {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}
        return {"player_1_wins" if (first, second) in wins else "player_2_wins": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return next_state

    def reward(self, state, joint_action, next_state, player):
        return 0.0

    def is_terminal(self, state):
        return state != "start"
'''


class PythonPOSGTests(unittest.TestCase):
    def test_g1_rollout_and_eda(self) -> None:
        result = run_posg_experiment(
            "RPS",
            model_name="test",
            code_generator=lambda description, model: RPS_SOURCE,
        )

        self.assertTrue(result["success"])
        self.assertEqual(len(result["rollout"]["states"]), 4)
        self.assertEqual(len(result["rollout"]["terminal_states"]), 3)
        self.assertEqual(len(result["rollout"]["transitions"]), 9)
        self.assertEqual(
            result["eda_summary"]["transitions"]["deterministic_transition_fraction"], 1.0
        )
        self.assertEqual(result["state_graph"].number_of_edges(), 3)

    def test_undefined_generated_variable_is_a_validation_failure(self) -> None:
        broken = RPS_SOURCE.replace(
            'return {"player_1_wins" if (first, second) in wins else "player_2_wins": 1.0}',
            'return {f"win_{player}": 1.0}',
        )
        result = run_posg_experiment(
            "broken",
            model_name="test",
            code_generator=lambda description, model: broken,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["stage"], "validation")
        self.assertIn("NameError", "\n".join(result["errors"]))

    def test_invalid_transition_probabilities_are_reported(self) -> None:
        class InvalidPOSG(AbstractPOSG):
            players = ["player_1", "player_2"]

            def initial_state(self):
                return "start"

            def legal_actions(self, state, player):
                return ["act"]

            def transition(self, state, joint_action):
                return {"end": 0.4}

            def observation(self, state, joint_action, next_state, player):
                return "observation"

            def reward(self, state, joint_action, next_state, player):
                return 0.0

            def is_terminal(self, state):
                return state == "end"

        validation = validate_posg(InvalidPOSG)

        self.assertFalse(validation["passed"])
        self.assertIn("sum to 0.4", "\n".join(validation["errors"]))

    def test_terminal_initial_state_is_rejected(self) -> None:
        class TerminalInitialPOSG(AbstractPOSG):
            players = ["player_1", "player_2"]

            def initial_state(self):
                return "finished"

            def legal_actions(self, state, player):
                return []

            def transition(self, state, joint_action):
                return {"finished": 1.0}

            def observation(self, state, joint_action, next_state, player):
                return "finished"

            def reward(self, state, joint_action, next_state, player):
                return 0.0

            def is_terminal(self, state):
                return True

        validation = validate_posg(TerminalInitialPOSG)

        self.assertFalse(validation["passed"])
        self.assertIn("Initial state", "\n".join(validation["errors"]))


if __name__ == "__main__":
    unittest.main()
