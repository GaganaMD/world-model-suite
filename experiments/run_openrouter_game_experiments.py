"""Run the G1--G9 generated-POSG evaluation suite through OpenRouter.

Results from one invocation are kept under a single timestamped directory:
experiments/openrouter/<run-id>/<model>/<case>/<sample>/.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import requests

# Make the repository package importable when this file is executed directly.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from world_model_eda import CORRECTED_PROMPT_TEMPLATE, ExperimentConfig, ExperimentRunner
from world_model_eda.experiment_runner import OllamaPOSGBackend, save_results_table


CASE_ROOT = REPO_ROOT / "data" / "Test_Cases" / "03_game"
ARTIFACT_ROOT = REPO_ROOT / "experiments" / "openrouter"
DEFAULT_MODELS = {
    "gpt_5_6_sol": "openai/gpt-5.6-sol",
    "claude_opus_5": "anthropic/claude-opus-5",
    "llama_3_3_70b": "meta-llama/llama-3.3-70b-instruct",
    "qwen_3_8_27b": "qwen/qwen3.8-27b",
    "deepseek_v4_flash": "deepseek/deepseek-v4-flash-0731",
}


def load_dotenv(path: Path = REPO_ROOT / ".env") -> None:
    """Load simple KEY=VALUE entries without adding a package dependency."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def game_descriptions(root: Path = CASE_ROOT) -> dict[str, str]:
    descriptions = {}
    for path in sorted(root.glob("game_G_*.md"), key=lambda item: int(item.name.split("_")[2])):
        case = f"G{int(path.name.split('_')[2])}"
        text = path.read_text(encoding="utf-8")
        match = re.search(
            r"(?:#+ )?LLM Input\s*\n+(.*?)(?:\n\s*(?:#+ )?Expected LLM Output|\Z)",
            text,
            re.DOTALL,
        )
        if not match:
            raise ValueError(f"Could not find LLM Input in {path}.")
        descriptions[case] = match.group(1).strip()
    if not descriptions:
        raise FileNotFoundError(f"No game cases found under {root}")
    return descriptions


class OpenRouterPOSGBackend:
    SYSTEM_PROMPT = OllamaPOSGBackend.SYSTEM_PROMPT

    def __init__(
        self,
        api_key: str,
        model_aliases: Mapping[str, str],
        *,
        timeout: float = 300,
        max_retries: int = 3,
        max_tokens: int = 8192,
    ) -> None:
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is empty. Add your key to the repository .env file.")
        self.api_key = api_key
        self.model_aliases = dict(model_aliases)
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_tokens = max_tokens

    def model_identifier(self, model: str) -> str:
        return self.model_aliases.get(model, model)

    def render_prompt(self, game_description: str) -> str:
        return CORRECTED_PROMPT_TEMPLATE.format(game_description=game_description)

    def artifact_prompt(self, game_description: str) -> str:
        return f"SYSTEM:\n{self.SYSTEM_PROMPT}\n\nUSER:\n{self.render_prompt(game_description)}\n"

    def __call__(self, game_description: str, model: str) -> str:
        payload = {
            "model": self.model_identifier(model),
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": self.render_prompt(game_description)},
            ],
            "temperature": 0,
            "max_tokens": self.max_tokens,
        }
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/world-model-suite",
                        "X-Title": "World Model Suite",
                    },
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                body = response.json()
                content = body["choices"][0]["message"].get("content")
                if not content:
                    raise RuntimeError(f"OpenRouter returned no message content: {body}")
                fenced = re.search(r"```(?:python)?\s*(.*?)\s*```", content, re.DOTALL)
                return fenced.group(1).strip() if fenced else content.strip()
            except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError, RuntimeError):
                if attempt == self.max_retries:
                    raise
                time.sleep(min(2 ** (attempt - 1), 8))
        raise AssertionError("unreachable")


def configured_models() -> dict[str, str]:
    configured = os.getenv("OPENROUTER_MODELS", "").strip()
    identifiers = [item.strip() for item in configured.split(",") if item.strip()]
    if not identifiers:
        return dict(DEFAULT_MODELS)
    return {re.sub(r"[^a-z0-9]+", "_", item.lower()).strip("_"): item for item in identifiers}


def run() -> tuple[Path, list[dict]]:
    load_dotenv()
    models = configured_models()
    run_id = "openrouter-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = ARTIFACT_ROOT / run_id
    if run_root.exists():
        raise FileExistsError(f"Refusing to overwrite existing run: {run_root}")

    backend = OpenRouterPOSGBackend(
        os.getenv("OPENROUTER_API_KEY", ""),
        models,
        timeout=float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "300")),
        max_retries=int(os.getenv("OPENROUTER_MAX_RETRIES", "3")),
        max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "8192")),
    )
    config = ExperimentConfig(
        models=list(models),
        cases=game_descriptions(),
        samples_per_case=int(os.getenv("OPENROUTER_SAMPLES_PER_CASE", "1")),
        experiment_id=run_id,
        prompt_variant="P2_corrected",
        artifact_root=run_root,
        profile_memory=True,
    )
    records = ExperimentRunner(config, generator=backend).run()
    save_results_table(records, run_root / "summary.json")
    (run_root / "run_config.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "models": models,
                "cases": list(config.cases),
                "samples_per_case": config.samples_per_case,
                "prompt_variant": config.prompt_variant,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return run_root, records


if __name__ == "__main__":
    destination, results = run()
    succeeded = sum(record["status"] == "success" for record in results)
    print(f"Completed {len(results)} generations ({succeeded} successful).")
    print(f"All results: {destination}")
