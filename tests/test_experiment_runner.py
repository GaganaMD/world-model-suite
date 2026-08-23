import json
import tempfile
import unittest
from pathlib import Path

from tests.test_python_posg import RPS_SOURCE
from world_model_eda import ExperimentConfig, ExperimentRunner, results_table, save_results_table
from world_model_eda.experiment_runner import PROMPT_TEMPLATE


class ExperimentRunnerTests(unittest.TestCase):
    def test_successful_profiled_run_saves_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = ExperimentConfig(
                models=["mock"],
                cases={"G1": "RPS"},
                artifact_root=Path(directory),
                profile_memory=True,
            )
            result = ExperimentRunner(
                config, generator=lambda description, model: RPS_SOURCE
            ).run()[0]

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["reachable_states"], 4)
            self.assertEqual(result["terminal_states"], 3)
            self.assertEqual(result["edges"], 3)
            self.assertIsNotNone(result["generation_seconds"])
            self.assertIsNotNone(result["execution_seconds"])
            self.assertIsNotNone(result["rollout_seconds"])
            self.assertIsNotNone(result["peak_memory_mb"])
            self.assertGreaterEqual(result["total_seconds"], result["generation_seconds"])
            artifact_dir = Path(result["artifact_dir"])
            self.assertTrue((artifact_dir / "generated.py").is_file())
            self.assertTrue((artifact_dir / "world_model.json").is_file())
            self.assertTrue((artifact_dir / "graph.png").is_file())
            self.assertEqual(
                json.loads((artifact_dir / "result.json").read_text(encoding="utf-8"))["status"],
                "success",
            )

    def test_failed_generation_preserves_failure_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = ExperimentConfig(
                models=["mock"], cases={"G9": "Blotto"}, artifact_root=Path(directory)
            )
            result = ExperimentRunner(
                config, generator=lambda description, model: "class GeneratedPOSG("
            ).run()[0]

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["failure_type"], "invalid_python")
            self.assertIsNotNone(result["generation_seconds"])
            self.assertIsNotNone(result["execution_seconds"])
            self.assertIsNone(result["rollout_seconds"])
            artifact_dir = Path(result["artifact_dir"])
            self.assertEqual((artifact_dir / "generated.py").read_text(encoding="utf-8"), "class GeneratedPOSG(")

    def test_compact_result_table_and_configuration_validation(self) -> None:
        with self.assertRaises(ValueError):
            ExperimentRunner(ExperimentConfig(models=["mock"], cases={}, samples_per_case=0))

        result = ExperimentRunner(
            ExperimentConfig(models=["mock"], cases={"G1": "RPS"}, save_artifacts=False),
            generator=lambda description, model: RPS_SOURCE,
        ).run()[0]
        table = results_table([result])

        self.assertEqual(table[0]["case"], "G1")
        self.assertNotIn("artifact_dir", table[0])
        with tempfile.TemporaryDirectory() as directory:
            path = save_results_table([result], Path(directory) / "summary.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))[0]["case"], "G1")

    def test_prompt_template_formats_with_skeleton(self) -> None:
        prompt = PROMPT_TEMPLATE.format(game_description="A small situation.")

        self.assertIn('return {"terminal": 1.0}', prompt)
        self.assertIn('not `{}`', prompt)


if __name__ == "__main__":
    unittest.main()
