"""Small, controlled compute-profiling runner for generated Python POSGs."""

from __future__ import annotations

import json
import re
import time
import tracemalloc
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

from .eda import WorldModelEDA
from .python_posg import (
    build_state_action_graph,
    build_state_graph,
    canonical_rollout_json,
    classify_failure,
    execute_generated_posg,
    rollout_world_model,
)


GenerationFunction = Callable[[str, str], str]


PROMPT_TEMPLATE = """Write executable Python inside a module where AbstractPOSG already exists.
Define only `class GeneratedPOSG(AbstractPOSG)`; do not import or redefine AbstractPOSG.

Every state identifier must be hashable. Prefer strings or tuples. Never use dictionaries, lists,
sets, numpy arrays, or another mutable container as initial states or transition keys.
`initial_state()` must return one concrete hashable state, for example `"s0"`, not `{{}}`.
`transition()` must return `Dict[hashable_state, float]` with finite non-negative probabilities
that sum to 1.0. `joint_action` is a dictionary keyed by explicit player IDs.

Use this interface shape, filling in situation-specific logic only:
class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["action"]
    def transition(self, state, joint_action): return {{"terminal": 1.0}}
    def observation(self, state, joint_action, next_state, player): return "observation"
    def reward(self, state, joint_action, next_state, player): return 0.0
    def is_terminal(self, state): return state == "terminal"

Implement every method with actual situation-specific behavior. legal_actions returns a list of
valid action identifiers; is_terminal returns bool; observation returns a valid observation; and
reward returns a number. Output only Python code, without Markdown fences.

SITUATION:
{game_description}"""


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for a controlled sequential pilot or small batch."""

    models: Sequence[str]
    cases: Mapping[str, str]
    samples_per_case: int = 1
    max_states: int = 10_000
    max_depth: int = 20
    seed: int = 42
    save_artifacts: bool = True
    artifact_root: Path = Path("experiments")
    profile_memory: bool = False


class OllamaPOSGBackend:
    """Model-name adapter for the project's existing local Ollama generation path."""

    DEFAULT_MODELS = {"qwen": "qwen2.5-coder:latest"}

    def __init__(
        self, model_aliases: Optional[Mapping[str, str]] = None, seed: int = 42
    ) -> None:
        self.model_aliases = {**self.DEFAULT_MODELS, **(model_aliases or {})}
        self.seed = seed

    def __call__(self, game_description: str, model: str) -> str:
        import ollama

        resolved_model = self.model_aliases.get(model, model)
        response = ollama.chat(
            model=resolved_model,
            messages=[
                {
                    "role": "system",
                    "content": "Return only a GeneratedPOSG implementation using the provided AbstractPOSG.",
                },
                {
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(game_description=game_description),
                },
            ],
            options={"temperature": 0.0, "seed": self.seed},
        )
        content = response["message"]["content"].strip()
        fenced = re.search(r"```(?:python)?\s*(.*?)\s*```", content, re.DOTALL)
        return fenced.group(1).strip() if fenced else content


class ExperimentRunner:
    """Run generated-Python POSG experiments while preserving partial failures."""

    def __init__(self, config: ExperimentConfig, generator: Optional[GenerationFunction] = None) -> None:
        if config.samples_per_case < 1:
            raise ValueError("samples_per_case must be at least one.")
        self.config = config
        self.artifact_root = Path(config.artifact_root)
        self.generator = generator or OllamaPOSGBackend(seed=config.seed)

    def run_case(self, model: str, case: str, description: str, sample: int) -> Dict[str, Any]:
        """Profile one generation through execution, rollout, graphing, and EDA."""
        result = self._base_result(model, case, sample)
        peak_memory_mb: Optional[float] = None
        if self.config.profile_memory:
            tracemalloc.start()
        total_start = time.perf_counter()
        source: Optional[str] = None
        try:
            generation_start = time.perf_counter()
            source = self.generator(description, model)
            result["generation_seconds"] = time.perf_counter() - generation_start
            result["_source"] = source

            execution_start = time.perf_counter()
            execution = execute_generated_posg(source)
            result["execution_seconds"] = time.perf_counter() - execution_start
            if not execution["success"]:
                self._fail(result, execution)
                return result

            # Contract/execution validation is represented by the exhaustive rollout below.
            # This preflight timing isolates the instance's public interface access.
            validation_start = time.perf_counter()
            players = execution["world_model"].players
            execution["world_model"].initial_state()
            if not isinstance(players, list) or not players:
                raise ValueError("players must be a non-empty list.")
            result["validation_seconds"] = time.perf_counter() - validation_start

            rollout_start = time.perf_counter()
            rollout = rollout_world_model(
                execution["world_model"],
                max_states=self.config.max_states,
                max_depth=self.config.max_depth,
            )
            result["rollout_seconds"] = time.perf_counter() - rollout_start
            if rollout["errors"]:
                self._fail(result, {"errors": rollout["errors"]})
                return result

            graph_start = time.perf_counter()
            state_graph = build_state_graph(rollout)
            state_action_graph = build_state_action_graph(rollout)
            result["graph_seconds"] = time.perf_counter() - graph_start

            eda_start = time.perf_counter()
            eda = WorldModelEDA.from_rollout(rollout)
            summary = eda.summary()
            result["eda_seconds"] = time.perf_counter() - eda_start
            result.update(self._metrics(summary))
            result["status"] = "success"
            result["_rollout"] = rollout
            result["_eda"] = eda
            result["_state_graph"] = state_graph
            result["_state_action_graph"] = state_action_graph
            return result
        except Exception as error:
            self._fail(result, {"errors": [f"{type(error).__name__}: {error}"]})
            if source is not None:
                result["_source"] = source
            return result
        finally:
            result["total_seconds"] = time.perf_counter() - total_start
            if self.config.profile_memory:
                _current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_memory_mb = peak / (1024 * 1024)
            result["peak_memory_mb"] = peak_memory_mb
            if self.config.save_artifacts:
                try:
                    result["artifact_dir"] = str(self._save_artifacts(result))
                except Exception as error:
                    result["artifact_error"] = f"{type(error).__name__}: {error}"
            self._strip_runtime_objects(result)

    def run(self) -> list[Dict[str, Any]]:
        """Run the configured cases sequentially; one failure never aborts the batch."""
        records = []
        for model in self.config.models:
            for case, description in self.config.cases.items():
                for sample in range(1, self.config.samples_per_case + 1):
                    records.append(self.run_case(model, case, description, sample))
        return records

    def _base_result(self, model: str, case: str, sample: int) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "case": case,
            "sample": sample,
            "status": "failed",
            "generation_seconds": None,
            "execution_seconds": None,
            "validation_seconds": None,
            "rollout_seconds": None,
            "graph_seconds": None,
            "eda_seconds": None,
            "total_seconds": None,
            "peak_memory_mb": None,
            "failure_type": None,
            "error_message": None,
            "artifact_dir": None,
        }

    @staticmethod
    def _metrics(summary: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "reachable_states": summary["states"]["state_count"],
            "terminal_states": summary["states"]["terminal_state_count"],
            "edges": summary["graph"]["edge_count"],
            "avg_branching": summary["states"]["mean_branching_factor"],
            "max_branching": summary["states"]["maximum_branching_factor"],
            "deterministic_fraction": summary["transitions"]["deterministic_transition_fraction"],
            "stochastic_fraction": summary["transitions"]["stochastic_transition_fraction"],
            "avg_entropy": summary["transitions"]["mean_transition_entropy"],
            "max_entropy": summary["transitions"]["maximum_transition_entropy"],
            "max_depth": summary["states"]["maximum_trajectory_depth"],
            "scc_count": summary["graph"]["strongly_connected_component_count"],
        }

    @staticmethod
    def _fail(result: Dict[str, Any], failure: Mapping[str, Any]) -> None:
        classification = classify_failure(failure)
        result.update(
            {
                "status": "failed",
                "failure_type": classification["failure_type"],
                "error_message": classification["error_message"],
            }
        )

    def _save_artifacts(self, result: Mapping[str, Any]) -> Path:
        directory = (
            self.artifact_root
            / str(result["model"])
            / str(result["case"])
            / f"sample_{int(result['sample']):03d}"
        )
        directory.mkdir(parents=True, exist_ok=True)
        result["artifact_dir"] = str(directory)
        source = result.get("_source")
        if source:
            (directory / "generated.py").write_text(source, encoding="utf-8")
        rollout = result.get("_rollout")
        if rollout:
            (directory / "world_model.json").write_text(
                canonical_rollout_json(rollout), encoding="utf-8"
            )
        eda = result.get("_eda")
        if eda:
            axis = eda.plot_state_graph()
            axis.figure.savefig(directory / "graph.png", dpi=180, bbox_inches="tight")
            import matplotlib.pyplot as plt

            plt.close(axis.figure)
        (directory / "result.json").write_text(
            json.dumps(self._json_safe(result), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return directory

    @staticmethod
    def _json_safe(record: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in record.items()
            if not key.startswith("_") and isinstance(value, (str, int, float, bool, type(None)))
        }

    @staticmethod
    def _strip_runtime_objects(result: Dict[str, Any]) -> None:
        for key in list(result):
            if key.startswith("_"):
                del result[key]


def results_table(records: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    """Return serializable compact result rows suitable for a notebook dataframe."""
    return [
        {
            key: value
            for key, value in record.items()
            if key not in {"artifact_dir"} and isinstance(value, (str, int, float, bool, type(None)))
        }
        for record in records
    ]


def save_results_table(records: Sequence[Mapping[str, Any]], path: str | Path) -> Path:
    """Persist a compact serializable experiment summary without runtime objects."""
    destination = Path(path)
    destination.write_text(
        json.dumps(results_table(records), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
