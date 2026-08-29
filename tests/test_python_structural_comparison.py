import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from world_model_eda import (
    AbstractPOSG,
    aggregate_experiment_artifacts,
    canonical_document_to_rollout,
    canonical_rollout_json,
    canonical_to_lane2_model,
    eda_metrics,
    export_aggregate_results,
    failure_taxonomy,
    load_reference_game_cases,
    metric_deltas,
    rollout_to_canonical_document,
    validate_posg,
)
from world_model_eda.python_structural_comparison import compare_rollouts


HAS_GAME_MATCHING = importlib.util.find_spec("game_match") is not None


def reference_rollout():
    validation = validate_posg(load_reference_game_cases("data/Test_Cases/03_game")["G1"])
    assert validation["passed"]
    return validation["rollout"]


class RenamedRPS(AbstractPOSG):
    @property
    def players(self):
        return ["alpha", "beta"]

    def initial_state(self):
        return "opening"

    def legal_actions(self, state, player):
        return [] if self.is_terminal(state) else ["a", "b", "c"]

    def transition(self, state, joint_action):
        first, second = joint_action["alpha"], joint_action["beta"]
        if first == second:
            return {"tie": 1.0}
        wins = {("a", "c"), ("b", "a"), ("c", "b")}
        return {"alpha_outcome" if (first, second) in wins else "beta_outcome": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return next_state

    def reward(self, state, joint_action, next_state, player):
        return 0.0

    def is_terminal(self, state):
        return state != "opening"


class MissingActionRPS(RenamedRPS):
    def legal_actions(self, state, player):
        return [] if self.is_terminal(state) else ["a", "b"]


class ExtraActionRPS(RenamedRPS):
    def legal_actions(self, state, player):
        return [] if self.is_terminal(state) else ["a", "b", "c", "d"]

    def transition(self, state, joint_action):
        if "d" in joint_action.values():
            return {"extra_outcome": 1.0}
        return super().transition(state, joint_action)


class StochasticRPS(RenamedRPS):
    def transition(self, state, joint_action):
        if joint_action["alpha"] == joint_action["beta"] == "a":
            return {"tie": 0.5, "alpha_outcome": 0.5}
        return super().transition(state, joint_action)


class MissingStateRPS(RenamedRPS):
    def transition(self, state, joint_action):
        if joint_action["alpha"] == joint_action["beta"]:
            return {"tie": 1.0}
        return {"alpha_outcome": 1.0}


class ChangedTransitionRPS(RenamedRPS):
    def transition(self, state, joint_action):
        first, second = joint_action["alpha"], joint_action["beta"]
        if (first, second) == ("a", "c"):
            return {"tie": 1.0}
        return super().transition(state, joint_action)


class PythonStructuralComparisonTests(unittest.TestCase):
    def test_canonical_conversion_round_trips_eda_shape(self) -> None:
        rollout = reference_rollout()
        document = rollout_to_canonical_document(rollout)
        restored = canonical_document_to_rollout(document)

        self.assertEqual(eda_metrics(rollout), eda_metrics(restored))
        lane2 = canonical_to_lane2_model(document)
        self.assertEqual([player["id"] for player in lane2["players"]], ["player_1", "player_2"])
        self.assertEqual(len(lane2["states"]), 4)
        self.assertEqual(len(lane2["initial"]), 1)

    def test_metric_deltas_report_raw_and_relative_error(self) -> None:
        deltas = metric_deltas({"states": 4, "avg_entropy": 0.0}, {"states": 5, "avg_entropy": 1.0})

        self.assertEqual(deltas["states_difference"], 1.0)
        self.assertEqual(deltas["states_relative_error"], 0.25)
        self.assertEqual(deltas["avg_entropy_difference"], 1.0)
        self.assertIsNone(deltas["avg_entropy_relative_error"])

    def test_aggregate_export_and_failure_taxonomy(self) -> None:
        rows = [
            {"case": "G1", "failure_type": "unhashable_state"},
            {
                "case": "G1",
                "failure_type": None,
                "semantic_reward_failure": True,
                "semantic_observation_failure": True,
            },
        ]
        counts = failure_taxonomy(rows)
        self.assertEqual(counts["unhashable_state"], 1)
        self.assertEqual(counts["semantic_reward_failure"], 1)
        self.assertEqual(counts["semantic_observation_failure"], 1)
        self.assertEqual(counts["syntax_error"], 0)
        with tempfile.TemporaryDirectory() as directory:
            paths = export_aggregate_results(
                rows,
                csv_path=Path(directory) / "aggregate.csv",
                json_path=Path(directory) / "aggregate.json",
                chart_path=Path(directory) / "failures.png",
            )
            self.assertTrue(paths["csv"].is_file())
            self.assertEqual(json.loads(paths["json"].read_text(encoding="utf-8")), rows)
            self.assertTrue(paths["chart"].is_file())
            self.assertTrue(paths["taxonomy_csv"].is_file())

    def test_aggregate_failure_row_preserves_reference_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "qwen" / "G1" / "sample_001"
            artifact.mkdir(parents=True)
            (artifact / "result.json").write_text(
                json.dumps(
                    {
                        "case": "G1",
                        "model": "qwen",
                        "sample": 1,
                        "status": "failed",
                        "failure_type": "unhashable_state",
                    }
                ),
                encoding="utf-8",
            )
            rows = aggregate_experiment_artifacts(directory)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["failure_type"], "unhashable_state")
            self.assertEqual(rows[0]["reference_states"], 4)
            self.assertEqual(rows[0]["structural_status"], "NOT_EVALUATED")

    @unittest.skipUnless(HAS_GAME_MATCHING, "game_matching is an optional Lane 2 dependency")
    def test_reference_self_comparison_and_renaming_invariance(self) -> None:
        reference = reference_rollout()
        renamed = validate_posg(RenamedRPS())["rollout"]

        self.assertEqual(compare_rollouts(reference, reference, sa_iters=1_000)["lane2"], 1.0)
        result = compare_rollouts(reference, renamed, sa_iters=1_000)
        self.assertEqual(result["lane2"], 1.0)
        self.assertEqual(result["structural_status"], "PASS")

    @unittest.skipUnless(HAS_GAME_MATCHING, "game_matching is an optional Lane 2 dependency")
    def test_missing_extra_and_stochastic_structure_score_lower(self) -> None:
        reference = reference_rollout()
        for posg in (
            MissingActionRPS(),
            ExtraActionRPS(),
            MissingStateRPS(),
            ChangedTransitionRPS(),
            StochasticRPS(),
        ):
            validation = validate_posg(posg)
            self.assertTrue(validation["passed"])
            result = compare_rollouts(reference, validation["rollout"], sa_iters=1_000)
            self.assertLess(result["lane2"], 1.0)
            self.assertEqual(result["structural_status"], "DIFFERENT")


if __name__ == "__main__":
    unittest.main()
