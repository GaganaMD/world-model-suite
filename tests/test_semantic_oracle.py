import unittest

from world_model_eda import AbstractPOSG, evaluate_g1_posg, evaluate_g1_source


class CorrectRPS(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return [] if self.is_terminal(state) else ["rock", "paper", "scissors"]

    def transition(self, state, joint_action):
        first, second = joint_action["player_1"], joint_action["player_2"]
        if first == second:
            return {"draw": 1.0}
        wins = {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}
        return {"player_1_wins" if (first, second) in wins else "player_2_wins": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return "draw" if next_state == "draw" else f"{next_state.replace('_', ' ')}"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "draw":
            return 0.0
        if next_state == "player_1_wins":
            return 1.0 if player == "player_1" else -1.0
        return -1.0 if player == "player_1" else 1.0

    def is_terminal(self, state):
        return state != "s0"


class SemanticOracleTests(unittest.TestCase):
    def test_known_correct_rps_passes(self) -> None:
        result = evaluate_g1_posg(CorrectRPS())

        self.assertEqual(result["structural_validity"], "PASS")
        self.assertEqual(result["semantic_validity"], "PASS")
        self.assertEqual(result["semantic_score"], 1.0)

    def test_incorrect_reward_fails_reward_check(self) -> None:
        class IncorrectRewardRPS(CorrectRPS):
            def reward(self, state, joint_action, next_state, player):
                return 0.0

        result = evaluate_g1_posg(IncorrectRewardRPS())

        self.assertEqual(result["semantic_validity"], "FAIL")
        self.assertEqual(result["checks"]["rewards"]["status"], "FAIL")

    def test_incorrect_transition_fails_transition_check(self) -> None:
        class IncorrectTransitionRPS(CorrectRPS):
            def transition(self, state, joint_action):
                first, second = joint_action["player_1"], joint_action["player_2"]
                return {"draw": 1.0} if first == "rock" else super().transition(state, joint_action)

        result = evaluate_g1_posg(IncorrectTransitionRPS())

        self.assertEqual(result["semantic_validity"], "FAIL")
        self.assertEqual(result["checks"]["transitions"]["status"], "FAIL")

    def test_incorrect_observation_is_flagged(self) -> None:
        class IncorrectObservationRPS(CorrectRPS):
            def observation(self, state, joint_action, next_state, player):
                if next_state == "draw":
                    return "draw"
                return f"{player} wins"

        result = evaluate_g1_posg(IncorrectObservationRPS())

        self.assertEqual(result["semantic_validity"], "FAIL")
        self.assertEqual(result["checks"]["observations"]["status"], "FAIL")

    def test_structurally_invalid_source_is_not_semantically_evaluated(self) -> None:
        result = evaluate_g1_source("class GeneratedPOSG(")

        self.assertEqual(result["structural_validity"], "FAIL")
        self.assertEqual(result["semantic_validity"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
