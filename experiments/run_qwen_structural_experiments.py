"""Run the controlled Qwen POSG structural-fidelity batches without overwriting artifacts.

This script intentionally uses the existing ExperimentRunner.  It records only
the requested small sweep, repeat subset, and G1 prompt ablation; it does not
claim a benchmark or repair generated source.
"""

from __future__ import annotations

from datetime import datetime, timezone
import re
from pathlib import Path

from world_model_eda import (
    ExperimentConfig,
    ExperimentRunner,
    OllamaPOSGBackend,
    WorldModelEDA,
    export_robustness_report,
    load_reference_game_cases,
    reference_deltas,
    validate_posg,
)
from world_model_eda.experiment_runner import PROMPT_TEMPLATE


CASE_ROOT = Path("data/Test_Cases/03_game")
ARTIFACT_ROOT = Path("experiments")
P1_REQUIREMENT = """

The generated POSG must be executable. States and transition keys must use
hashable string or tuple identifiers only."""

P2_REQUIREMENT = P1_REQUIREMENT + """

For explicitly zero-sum games, rewards must be (+1,-1), (-1,+1), or (0,0)
as appropriate, and observations must identify the same outcome consistently
for each player."""


def game_descriptions(root: Path = CASE_ROOT) -> dict[str, str]:
    """Load each case's LLM Input section without exposing expected JSON."""
    descriptions = {}
    for path in sorted(root.glob("game_G_*.md")):
        case = f"G{int(path.name.split('_')[2])}"
        text = path.read_text(encoding="utf-8")
        match = re.search(r"(?:#+ )?LLM Input\s*\n+(.*?)(?:\n\s*(?:#+ )?Expected LLM Output|\Z)", text, re.DOTALL)
        if not match:
            raise ValueError(f"Could not find LLM Input in {path}.")
        descriptions[case] = match.group(1).strip()
    return descriptions


def run_batch(
    *,
    model: str,
    cases: dict[str, str],
    samples_per_case: int,
    backend: OllamaPOSGBackend,
    experiment_id: str,
    prompt_variant: str,
    artifact_root: Path,
) -> list[dict]:
    """Run sequentially with a separate non-overlapping range for every case."""
    records = []
    for case, description in cases.items():
        config = ExperimentConfig(
            models=[model],
            cases={case: description},
            samples_per_case=samples_per_case,
            sample_start=1,
            experiment_id=experiment_id,
            prompt_variant=prompt_variant,
            model_identifier=backend.model_identifier(model),
            artifact_root=artifact_root,
            profile_memory=True,
        )
        records.extend(ExperimentRunner(config, generator=backend).run())
    return records


def new_experiment_id() -> str:
    """Generate a run ID that cannot reuse an existing experiment directory."""
    identifier = "qwen-robustness-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = ARTIFACT_ROOT / "robustness" / identifier
    if destination.exists():
        raise FileExistsError(f"Experiment ID already exists: {identifier}")
    return identifier


def reference_metrics() -> dict[str, dict]:
    """Extract the same simple descriptors from the executable G1--G9 fixtures."""
    metrics = {}
    for case, posg in load_reference_game_cases(CASE_ROOT).items():
        validation = validate_posg(posg)
        if not validation["passed"]:
            raise ValueError(f"Reference fixture {case} failed validation: {validation['errors']}")
        summary = WorldModelEDA.from_rollout(validation["rollout"]).summary()
        metrics[case] = {
            "reachable_states": summary["states"]["state_count"],
            "terminal_states": summary["states"]["terminal_state_count"],
            "edges": summary["graph"]["edge_count"],
            "max_depth": summary["states"]["maximum_trajectory_depth"],
            "avg_branching": summary["states"]["mean_branching_factor"],
            "deterministic_fraction": summary["transitions"]["deterministic_transition_fraction"],
            "stochastic_fraction": summary["transitions"]["stochastic_transition_fraction"],
            "avg_entropy": summary["transitions"]["mean_transition_entropy"],
        }
    return metrics


def run_requested_experiments(samples_per_condition: int = 5) -> list[dict]:
    """Execute G1--G9 x N baseline and G1/G9 x N for controlled P0/P1/P2 prompts."""
    descriptions = game_descriptions()
    experiment_id = new_experiment_id()
    artifact_root = ARTIFACT_ROOT / "robustness" / experiment_id
    baseline = OllamaPOSGBackend(model_aliases={"qwen_p0": "qwen2.5-coder:latest"})
    records = run_batch(
        model="qwen_p0",
        cases=descriptions,
        samples_per_case=samples_per_condition,
        backend=baseline,
        experiment_id=experiment_id,
        prompt_variant="P0",
        artifact_root=artifact_root,
    )
    p1 = OllamaPOSGBackend(
        model_aliases={"qwen_p1": "qwen2.5-coder:latest"},
        prompt_template=PROMPT_TEMPLATE + P1_REQUIREMENT,
    )
    p2 = OllamaPOSGBackend(
        model_aliases={"qwen_p2": "qwen2.5-coder:latest"},
        prompt_template=PROMPT_TEMPLATE + P2_REQUIREMENT,
    )
    for variant, backend in (("P1", p1), ("P2", p2)):
        records.extend(
            run_batch(
                model=f"qwen_{variant.lower()}",
                cases={case: descriptions[case] for case in ("G1", "G9")},
                samples_per_case=samples_per_condition,
                backend=backend,
                experiment_id=experiment_id,
                prompt_variant=variant,
                artifact_root=artifact_root,
            )
        )
    export_robustness_report(reference_deltas(records, reference_metrics()), artifact_root / "analysis")
    return records


if __name__ == "__main__":
    records = run_requested_experiments()
    for record in records:
        print(
            record["model"],
            record["case"],
            record["sample"],
            record["status"],
            record.get("failure_type", ""),
        )
