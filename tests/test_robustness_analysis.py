import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_python_posg import RPS_SOURCE
from world_model_eda import (
    ExperimentConfig,
    ExperimentRunner,
    export_robustness_report,
    reference_deltas,
    structural_signature,
    summarize_variability,
)


class RobustnessAnalysisTests(unittest.TestCase):
    def test_repeated_results_aggregate_and_signature_is_deterministic(self) -> None:
        records = [
            {
                "model": "mock",
                "case": "G1",
                "prompt_variant": "P0",
                "sample": sample,
                "status": "success",
                "generation_status": "success",
                "structural_validation_status": "success",
                "rollout_status": "success",
                "reachable_states": 4,
                "terminal_states": 3,
                "edges": 3,
                "max_depth": 1,
                "avg_branching": 2.25,
                "deterministic_fraction": 1.0,
                "stochastic_fraction": 0.0,
                "avg_entropy": 0.0,
            }
            for sample in (1, 2)
        ]
        summaries = summarize_variability(records)

        self.assertEqual(structural_signature(records[0]), structural_signature(records[1]))
        self.assertEqual(summaries[0]["structural_validation_success_rate"], 1.0)
        self.assertEqual(summaries[0]["same_signature_proportion"], 1.0)
        self.assertEqual(summaries[0]["stddev_reachable_states"], 0.0)

    def test_failed_runs_do_not_contribute_to_numeric_statistics(self) -> None:
        records = [
            {
                "model": "mock", "case": "G9", "prompt_variant": "P0", "status": "failed",
                "generation_status": "success", "structural_validation_status": "failed",
                "rollout_status": "failed", "failure_type": "unhashable_state",
            },
            {
                "model": "mock", "case": "G9", "prompt_variant": "P0", "status": "success",
                "generation_status": "success", "structural_validation_status": "success",
                "rollout_status": "success", "reachable_states": 4, "terminal_states": 3,
                "edges": 3, "max_depth": 1, "avg_branching": 2.25,
                "deterministic_fraction": 1.0, "stochastic_fraction": 0.0, "avg_entropy": 0.0,
            },
        ]
        summary = summarize_variability(records)[0]

        self.assertEqual(summary["attempts"], 2)
        self.assertEqual(summary["mean_reachable_states"], 4.0)
        self.assertEqual(summary["failure_mode_frequencies"], {"unhashable_state": 1})

    def test_artifacts_preserve_prompt_and_refuse_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = ExperimentConfig(
                models=["mock"],
                cases={"G1": "RPS"},
                prompt_variant="P2",
                prompt_text="Prompt for {game_description}",
                artifact_root=Path(directory),
            )
            runner = ExperimentRunner(config, generator=lambda _description, _model: RPS_SOURCE)
            result = runner.run()[0]
            artifact_dir = Path(result["artifact_dir"])

            self.assertEqual((artifact_dir / "prompt.txt").read_text(encoding="utf-8"), "Prompt for RPS")
            self.assertEqual(json.loads((artifact_dir / "result.json").read_text())["prompt_variant"], "P2")
            report = export_robustness_report([result], Path(directory) / "analysis")
            self.assertIn(
                "## G1 sample comparison",
                report["summary_markdown"].read_text(encoding="utf-8"),
            )
            repeated = runner.run()[0]
            self.assertIn("FileExistsError", repeated["artifact_error"])
            self.assertEqual(
                (artifact_dir / "prompt.txt").read_text(encoding="utf-8"), "Prompt for RPS"
            )

    def test_report_handles_missing_world_model_and_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            records = [{
                "model": "mock", "case": "G9", "sample": 1, "prompt_variant": "P0",
                "status": "failed", "generation_status": "success",
                "structural_validation_status": "failed", "rollout_status": "failed",
                "artifact_dir": str(Path(directory) / "missing"), "failure_type": "invalid_actions",
            }]
            paths = export_robustness_report(records, Path(directory) / "analysis")

            self.assertTrue(paths["records_csv"].is_file())
            self.assertTrue(paths["plot"].is_file())
            with self.assertRaises(FileExistsError):
                export_robustness_report(records, Path(directory) / "analysis")

    def test_reference_deltas_apply_only_to_successful_records(self) -> None:
        rows = reference_deltas(
            [
                {"case": "G1", "status": "success", "reachable_states": 5, "avg_entropy": 0.0},
                {"case": "G1", "status": "failed", "reachable_states": 99},
            ],
            {"G1": {"reachable_states": 4, "avg_entropy": 0.0}},
        )

        self.assertEqual(rows[0]["reachable_states_difference"], 1)
        self.assertNotIn("reachable_states_difference", rows[1])

    def test_structurally_valid_rollout_contributes_after_downstream_failure(self) -> None:
        summary = summarize_variability(
            [{
                "model": "mock", "case": "G6", "prompt_variant": "P0", "status": "failed",
                "structural_validation_status": "success", "rollout_status": "success",
                "reachable_states": 4, "terminal_states": 3, "edges": 3, "max_depth": 1,
                "avg_branching": 2.25, "deterministic_fraction": 1.0,
                "stochastic_fraction": 0.0, "avg_entropy": 0.0,
            }]
        )[0]

        self.assertEqual(summary["structurally_valid_samples"], 1)
        self.assertEqual(summary["same_signature_proportion"], 1.0)

    def test_successful_rollout_is_persisted_when_graphing_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runner = ExperimentRunner(
                ExperimentConfig(models=["mock"], cases={"G1": "RPS"}, artifact_root=Path(directory)),
                generator=lambda _description, _model: RPS_SOURCE,
            )
            with patch(
                "world_model_eda.experiment_runner.build_state_graph",
                side_effect=RuntimeError("graph failure"),
            ):
                result = runner.run()[0]

            artifact_dir = Path(result["artifact_dir"])
            self.assertEqual(result["rollout_status"], "success")
            self.assertEqual(result["status"], "failed")
            self.assertTrue((artifact_dir / "world_model.json").is_file())
            self.assertFalse((artifact_dir / "graph.png").exists())


if __name__ == "__main__":
    unittest.main()
