import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.run_openrouter_game_experiments import (
    DEFAULT_MODELS,
    OpenRouterPOSGBackend,
    configured_models,
    load_dotenv,
)


class OpenRouterExperimentTests(unittest.TestCase):
    def test_default_model_set_contains_requested_five(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(configured_models(), DEFAULT_MODELS)

    def test_environment_can_override_models(self) -> None:
        with patch.dict(os.environ, {"OPENROUTER_MODELS": "vendor/a, vendor/b"}, clear=True):
            self.assertEqual(configured_models(), {"vendor_a": "vendor/a", "vendor_b": "vendor/b"})

    def test_dotenv_does_not_overwrite_existing_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text("OPENROUTER_API_KEY=from-file\n", encoding="utf-8")
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "existing"}, clear=True):
                load_dotenv(path)
                self.assertEqual(os.environ["OPENROUTER_API_KEY"], "existing")

    def test_backend_rejects_empty_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "OPENROUTER_API_KEY is empty"):
            OpenRouterPOSGBackend("", DEFAULT_MODELS)


if __name__ == "__main__":
    unittest.main()

