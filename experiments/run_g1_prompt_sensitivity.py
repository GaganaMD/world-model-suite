"""Run the controlled G1 P0/P1/P2 prompt-sensitivity experiment."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from experiments.run_qwen_structural_experiments import game_descriptions, reference_metrics
from world_model_eda import (
    CORRECTED_PROMPT_TEMPLATE,
    ExperimentConfig,
    ExperimentRunner,
    OllamaPOSGBackend,
    export_robustness_report,
    reference_deltas,
)
from world_model_eda.experiment_runner import PROMPT_TEMPLATE


P2_SEMANTIC_REQUIREMENT = """

Semantic consistency requirement:
- Rewards and observations must be calculated from the actual transition
  outcome and requested declared player, and must be mutually consistent.
- Do not add stochastic loops, extra rounds, or state transitions unless the
  natural-language situation explicitly requires them.
"""


def run_variant(
    *,
    experiment_id: str,
    root: Path,
    variant: str,
    prompt_template: str,
    samples: int,
    seed: int = 42,
    generator_factory: Optional[Callable[[OllamaPOSGBackend], Callable[[str, str], str]]] = None,
) -> list[dict]:
    """Run independent G1 requests with fixed, recorded per-sample seeds."""
    records = []
    description = game_descriptions()["G1"]
    for sample in range(1, samples + 1):
        backend = OllamaPOSGBackend(
            model_aliases={"qwen": "qwen2.5-coder:latest"},
            seed=seed + sample - 1,
            prompt_template=prompt_template,
        )
        records.extend(
            ExperimentRunner(
                ExperimentConfig(
                    models=["qwen"],
                    cases={"G1": description},
                    samples_per_case=1,
                    sample_start=sample,
                    experiment_id=experiment_id,
                    prompt_variant=variant,
                    model_identifier=backend.model_identifier("qwen"),
                    artifact_root=root / variant,
                    profile_memory=True,
                    seed=seed + sample - 1,
                ),
                generator=generator_factory(backend) if generator_factory else backend,
            ).run()
        )
    return records


def run_g1_prompt_sensitivity(samples: int = 5) -> list[dict]:
    """Run five P0, P1, and P2 generations, then export a descriptive comparison."""
    experiment_id = "qwen-g1-prompt-sensitivity-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path("experiments") / "prompt_sensitivity" / experiment_id
    variants = (
        ("P0", PROMPT_TEMPLATE),
        ("P1", CORRECTED_PROMPT_TEMPLATE),
        ("P2", CORRECTED_PROMPT_TEMPLATE + P2_SEMANTIC_REQUIREMENT),
    )
    records = []
    for variant, prompt_template in variants:
        records.extend(
            run_variant(
                experiment_id=experiment_id,
                root=root,
                variant=variant,
                prompt_template=prompt_template,
                samples=samples,
            )
        )
    export_robustness_report(reference_deltas(records, reference_metrics()), root / "analysis")
    return records


if __name__ == "__main__":
    for result in run_g1_prompt_sensitivity():
        print(
            result["prompt_variant"],
            result["sample"],
            result["generation_seed"],
            result["generation_status"],
            result["execution_status"],
            result["structural_validation_status"],
            result["rollout_status"],
            result["graph_status"],
            result["status"],
            result["failure_type"],
            result["total_seconds"],
        )
