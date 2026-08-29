"""Run the isolated G1 P2_PLUS horizon-and-dynamics diagnostic."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from experiments.run_g1_prompt_sensitivity import P2_SEMANTIC_REQUIREMENT, run_variant
from experiments.run_qwen_structural_experiments import reference_metrics
from world_model_eda import CORRECTED_PROMPT_TEMPLATE, export_robustness_report, reference_deltas


P2_PLUS_HORIZON_REQUIREMENT = """

Decision-horizon and transition requirement:
- Model only the decision horizon explicitly stated in the situation. If it
  describes one round, episode, or interaction, do not invent additional
  rounds, repeated cycles, or return transitions.
- Do not add stochastic transitions merely to make the environment more
  complex. Every legal action profile must transition according to the
  dynamics described in the situation.
- If an action ends the stated interaction, transition directly to the
  appropriate terminal outcome state. Rewards must correspond to that actual
  resulting state.
- Do not invent game-specific rules absent from the natural-language situation.
"""


def run_p2_plus_g1(samples: int = 5) -> list[dict]:
    """Generate five independent G1 P2_PLUS samples and export their analysis."""
    experiment_id = "qwen-g1-p2plus-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path("experiments") / "prompt_sensitivity" / experiment_id
    records = run_variant(
        experiment_id=experiment_id,
        root=root,
        variant="P2_PLUS",
        prompt_template=(
            CORRECTED_PROMPT_TEMPLATE + P2_SEMANTIC_REQUIREMENT + P2_PLUS_HORIZON_REQUIREMENT
        ),
        samples=samples,
    )
    export_robustness_report(reference_deltas(records, reference_metrics()), root / "analysis")
    return records


if __name__ == "__main__":
    for result in run_p2_plus_g1():
        print(
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
