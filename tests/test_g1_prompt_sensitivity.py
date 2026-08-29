import unittest
import tempfile
from pathlib import Path

from experiments.run_g1_prompt_sensitivity import run_variant
from experiments.run_g1_p2plus_experiment import P2_PLUS_HORIZON_REQUIREMENT
from tests.test_python_posg import RPS_SOURCE


class G1PromptSensitivityTests(unittest.TestCase):
    def test_p2_plus_horizon_instruction_is_general(self) -> None:
        self.assertIn("decision horizon explicitly stated", P2_PLUS_HORIZON_REQUIREMENT)
        self.assertIn("appropriate terminal outcome state", P2_PLUS_HORIZON_REQUIREMENT)
        self.assertNotIn("rock", P2_PLUS_HORIZON_REQUIREMENT.lower())
        self.assertNotIn("paper", P2_PLUS_HORIZON_REQUIREMENT.lower())
        self.assertNotIn("scissors", P2_PLUS_HORIZON_REQUIREMENT.lower())

    def test_variant_preserves_distinct_recorded_sample_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            records = run_variant(
                experiment_id="test",
                root=Path(directory),
                variant="P1",
                prompt_template="Prompt: {game_description}",
                samples=3,
                seed=17,
                generator_factory=lambda _backend: lambda _description, _model: RPS_SOURCE,
            )
            self.assertEqual([record["generation_seed"] for record in records], [17, 18, 19])
            self.assertTrue((Path(directory) / "P1" / "qwen" / "G1" / "sample_003").is_dir())


if __name__ == "__main__":
    unittest.main()
