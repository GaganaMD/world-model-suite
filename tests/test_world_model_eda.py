import unittest

from examples.game_eda import RPS
from world_model_eda import WorldModelEDA


class WorldModelEDATests(unittest.TestCase):
    def test_rps_structure_and_outcome_compression(self) -> None:
        analysis = WorldModelEDA.from_dict(RPS)

        self.assertEqual(analysis.state_statistics()["state_count"], 4)
        self.assertEqual(analysis.state_statistics()["terminal_state_count"], 3)
        self.assertEqual(analysis.action_statistics()["joint_action_count"], 9)
        self.assertAlmostEqual(analysis.action_statistics()["outcome_compression"], 3 / 9)
        self.assertEqual(analysis.transition_statistics()["deterministic_transition_fraction"], 1.0)
        self.assertEqual(analysis.terminal_statistics()["distance_to_terminal"]["s0"], 1)

    def test_stochastic_transitions_have_entropy(self) -> None:
        analysis = WorldModelEDA.from_dict(
            {
                "players": [{"id": "p1"}, {"id": "p2"}],
                "initial_state": "start",
                "states": {"start": {}, "heads": {"terminal": True}, "tails": {"terminal": True}},
                "actions": {"start": {"p1": ["flip"], "p2": ["flip"]}},
                "transition_probabilities": {
                    "start": {"flip+flip": {"heads": 0.5, "tails": 0.5}}
                },
            }
        )

        self.assertEqual(analysis.transition_statistics()["stochastic_transition_fraction"], 1.0)
        self.assertAlmostEqual(analysis.entropy_analysis()["'start' | p1:flip + p2:flip"], 1.0)

    def test_posg_enumeration_combines_observation_outcomes(self) -> None:
        class TinyPOSG:
            players = {"p1": {}, "p2": {}}
            initial_state = "start"

            @staticmethod
            def is_terminal(state: str) -> bool:
                return state == "end"

            @staticmethod
            def legal_actions(state: str, player: str) -> list[str]:
                return ["go"]

            @staticmethod
            def transition_kernel(state: str, actions: dict[str, str]) -> dict[tuple[str, str], float]:
                return {("end", "p1_observation"): 0.4, ("end", "p2_observation"): 0.6}

        analysis = WorldModelEDA.from_posg(TinyPOSG())

        self.assertEqual(analysis.extract_states(), ["end", "start"])
        self.assertEqual(analysis.transition_statistics()["average_transition_branching"], 1.0)
        self.assertEqual(analysis.extract_transitions()[0]["probability"], 1.0)

    def test_multi_step_depth_and_delimited_actions(self) -> None:
        analysis = WorldModelEDA.from_dict(
            {
                "players": [{"id": "p1"}, {"id": "p2"}],
                "initial_state": "start",
                "states": {
                    "start": {},
                    "middle": {},
                    "end": {"terminal": True},
                },
                "actions": {
                    "start": {"p1": ["0+3"], "p2": ["0+3"]},
                    "middle": {"nature": ["finish"]},
                },
                "transition_probabilities": {
                    "start": {"0+3+0+3": {"middle": 1.0}},
                    "middle": {"finish": {"end": 1.0}},
                },
            }
        )

        self.assertEqual(analysis.extract_transitions()[0]["actions"], {"p1": "0+3", "p2": "0+3"})
        self.assertEqual(analysis.state_statistics()["maximum_trajectory_depth"], 2)


if __name__ == "__main__":
    unittest.main()
