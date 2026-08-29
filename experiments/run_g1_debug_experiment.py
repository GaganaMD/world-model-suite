"""Run the isolated corrected G1 diagnosis without touching baseline artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from experiments.run_qwen_structural_experiments import game_descriptions, reference_metrics
from world_model_eda import (
    CORRECTED_PROMPT_TEMPLATE,
    ExperimentConfig,
    ExperimentRunner,
    OllamaPOSGBackend,
    export_robustness_report,
    reference_deltas,
)


def run_corrected_g1(samples: int = 5) -> list[dict]:
    """Generate five G1 samples using the general interface-contract correction."""
    experiment_id = "qwen-g1-debug-corrected-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path("experiments") / "debug" / experiment_id
    backend = OllamaPOSGBackend(
        model_aliases={"qwen_debug": "qwen2.5-coder:latest"},
        prompt_template=CORRECTED_PROMPT_TEMPLATE,
    )
    records = ExperimentRunner(
        ExperimentConfig(
            models=["qwen_debug"],
            cases={"G1": game_descriptions()["G1"]},
            samples_per_case=samples,
            experiment_id=experiment_id,
            prompt_variant="P_debug_mapping_contract",
            model_identifier=backend.model_identifier("qwen_debug"),
            artifact_root=root,
            profile_memory=True,
        ),
        generator=backend,
    ).run()
    export_robustness_report(reference_deltas(records, reference_metrics()), root / "analysis")
    return records


if __name__ == "__main__":
    for result in run_corrected_g1():
        print(
            result["sample"],
            result["generation_status"],
            result["execution_status"],
            result["structural_validation_status"],
            result["rollout_status"],
            result["graph_status"],
            result["status"],
            result["failure_type"],
            result["total_seconds"],
        )
