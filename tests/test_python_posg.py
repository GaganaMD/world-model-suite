import json
import tempfile
import unittest
from pathlib import Path

from world_model_eda import (
    AbstractPOSG,
    batch_posg_cases,
    canonical_rollout_json,
    export_rollout_json,
    load_reference_game_cases,
    run_posg_experiment,
    validate_posg,
)


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
        canonical = canonical_rollout_json(result["rollout"])
        self.assertEqual(canonical, canonical_rollout_json(result["rollout"]))
        exported = json.loads(canonical)
        self.assertEqual(len(exported["states"]), 4)
        self.assertEqual(len(exported["transitions"]), 9)
        self.assertEqual(len(result["action_influence"]["player_1"]), 9)
        self.assertTrue(
            all(
                item["total_variation_distance"] == 1.0
                for item in result["action_influence"]["player_1"]
            )
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = export_rollout_json(result["rollout"], Path(directory) / "g1.json")
            self.assertEqual(destination.read_text(encoding="utf-8"), canonical)

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

    def test_unhashable_initial_state_has_actionable_diagnostic(self) -> None:
        class UnhashableInitialPOSG(AbstractPOSG):
            players = ["player_1", "player_2"]

            def initial_state(self):
                return {}

            def legal_actions(self, state, player):
                return ["act"]

            def transition(self, state, joint_action):
                return {"end": 1.0}

            def observation(self, state, joint_action, next_state, player):
                return "observation"

            def reward(self, state, joint_action, next_state, player):
                return 0.0

            def is_terminal(self, state):
                return False

        validation = validate_posg(UnhashableInitialPOSG)

        self.assertFalse(validation["passed"])
        self.assertIn("initial_state is not hashable", "\n".join(validation["errors"]))

    def test_all_reference_game_cases_roll_out(self) -> None:
        rows = batch_posg_cases(load_reference_game_cases("data/Test_Cases/03_game"))

        self.assertEqual([row["case"] for row in rows], [f"G{number}" for number in range(1, 10)])
        self.assertTrue(all(row["status"] == "success" for row in rows))
        g1 = rows[0]
        self.assertEqual(
            (g1["states"], g1["terminal_states"], g1["avg_branching"], g1["edges"]),
            (4, 3, 2.25, 3),
        )


if __name__ == "__main__":
    unittest.main()
