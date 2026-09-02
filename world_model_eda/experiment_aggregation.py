"""Aggregate persisted Python POSG artifacts against executable references."""

from __future__ import annotations

import csv
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from .python_posg import validate_posg
from .python_structural_comparison import comparison_row
from .reference_games import load_reference_game_cases
from .semantic_oracle import evaluate_g1_source


FAILURE_TAXONOMY = {
    "invalid_python": "syntax_error",
    "interface_failure": "execution_error",
    "unhashable_state": "unhashable_state",
    "invalid_transition": "invalid_transition",
    "invalid_probability": "invalid_probability",
    "invalid_actions": "invalid_action",
    "rollout_limit": "nontermination",
    "observation_failure": "execution_error",
    "reward_failure": "execution_error",
    "invalid_terminal_structure": "structural_failure",
    "other": "execution_error",
}
FAILURE_CATEGORIES = (
    "syntax_error",
    "execution_error",
    "invalid_state",
    "unhashable_state",
    "invalid_transition",
    "invalid_probability",
    "invalid_action",
    "nontermination",
    "structural_failure",
    "semantic_reward_failure",
    "semantic_observation_failure",
    "other",
)


def canonical_document_to_rollout(document: Mapping[str, Any]) -> Dict[str, Any]:
    """Restore the rollout shape needed by EDA from canonical artifact JSON."""
    states = {
        state["id"]: {"terminal": bool(state["terminal"]), "depth": state["depth"]}
        for state in document["states"]
    }
    return {
        "players": list(document["players"]),
        "initial_distribution": {
            entry["state"]: float(entry["probability"])
            for entry in document["initial_distribution"]
        },
        "states": states,
        "actions": {
            state["id"]: dict(state.get("actions", {}))
            for state in document["states"]
            if not state["terminal"]
        },
        "transitions": [
            {
                "state": transition["state"],
                "joint_action": dict(transition["joint_action"]),
                "outcomes": [
                    {
                        "next_state": outcome["next_state"],
                        "probability": float(outcome["probability"]),
                        "observations": dict(outcome["observations"]),
                        "rewards": dict(outcome["rewards"]),
                    }
                    for outcome in transition["outcomes"]
                ],
            }
            for transition in document["transitions"]
        ],
        "terminal_states": [state_id for state_id, state in states.items() if state["terminal"]],
        "warnings": list(document.get("warnings", [])),
        "errors": list(document.get("errors", [])),
        "truncated": bool(document.get("truncated", False)),
    }


def load_artifact_rollout(path: str | Path) -> Dict[str, Any]:
    """Load a persisted canonical world model artifact as an EDA rollout."""
    return canonical_document_to_rollout(json.loads(Path(path).read_text(encoding="utf-8")))


def _reference_rollouts(reference_root: str | Path) -> Dict[str, Dict[str, Any]]:
    rollouts = {}
    for case, posg in load_reference_game_cases(reference_root).items():
        validation = validate_posg(posg)
        if not validation["passed"]:
            raise ValueError(f"Reference fixture {case} did not validate: {validation['errors']}")
        rollouts[case] = validation["rollout"]
    return rollouts


def _normalized_failure(failure_type: str | None, error_message: str | None) -> str | None:
    """Normalize historical runner categories without losing the raw value."""
    if failure_type == "other" and error_message:
        if any(
            marker in error_message
            for marker in ("NameError", "TypeError", "KeyError", "IndexError", "AttributeError")
        ):
            return "execution_error"
    return FAILURE_TAXONOMY.get(failure_type or "", failure_type or "other")


def aggregate_experiment_artifacts(
    artifact_root: str | Path = "experiments",
    *,
    reference_root: str | Path = "data/Test_Cases/03_game",
) -> list[Dict[str, Any]]:
    """Load persisted runs and compare every successful artifact to its fixture."""
    references = _reference_rollouts(reference_root)
    rows: list[Dict[str, Any]] = []
    for result_path in sorted(Path(artifact_root).glob("*/*/sample_*/result.json")):
        result = json.loads(result_path.read_text(encoding="utf-8"))
        case = str(result["case"])
        if case not in references:
            continue
        world_model_path = result_path.with_name("world_model.json")
        generated = load_artifact_rollout(world_model_path) if world_model_path.is_file() else None
        row = comparison_row(
            case=case,
            model=str(result["model"]),
            sample=int(result["sample"]),
            reference_rollout=references[case],
            generated_rollout=generated,
            failure_type=_normalized_failure(result.get("failure_type"), result.get("error_message")),
        )
        row["artifact_dir"] = str(result_path.parent)
        row["recorded_failure_type"] = result.get("failure_type")
        row["generation_seconds"] = result.get("generation_seconds")
        row["total_seconds"] = result.get("total_seconds")
        if case == "G1" and (source_path := result_path.with_name("generated.py")).is_file():
            semantic = evaluate_g1_source(source_path.read_text(encoding="utf-8"))
            row["semantic_validity"] = semantic["semantic_validity"]
            row["semantic_score"] = semantic["semantic_score"]
            checks = semantic.get("checks", {})
            row["semantic_reward_status"] = checks.get("rewards", {}).get("status")
            row["semantic_observation_status"] = checks.get("observations", {}).get("status")
            if semantic["semantic_validity"] == "FAIL":
                if row["semantic_reward_status"] == "FAIL":
                    row["semantic_reward_failure"] = True
                if row["semantic_observation_status"] == "FAIL":
                    row["semantic_observation_failure"] = True
        rows.append(row)
    return rows


def failure_taxonomy(rows: Iterable[Mapping[str, Any]]) -> Dict[str, int]:
    """Count mechanical and semantic failures without conflating their layers."""
    counts: Counter[str] = Counter({category: 0 for category in FAILURE_CATEGORIES})
    for row in rows:
        if row.get("failure_type"):
            counts[str(row["failure_type"])] += 1
        if row.get("semantic_reward_failure"):
            counts["semantic_reward_failure"] += 1
        if row.get("semantic_observation_failure"):
            counts["semantic_observation_failure"] += 1
    return dict(counts)


def export_aggregate_results(
    rows: Sequence[Mapping[str, Any]],
    *,
    csv_path: str | Path = "experiments/aggregate_results.csv",
    json_path: str | Path = "experiments/aggregate_results.json",
    chart_path: str | Path = "experiments/failure_taxonomy.png",
    taxonomy_csv_path: str | Path = "experiments/failure_taxonomy.csv",
) -> Dict[str, Path]:
    """Export a rectangular results table, JSON copy, and failure bar chart."""
    csv_destination, json_destination, chart_destination, taxonomy_destination = (
        Path(csv_path),
        Path(json_path),
        Path(chart_path),
        Path(taxonomy_csv_path),
    )
    for destination in (csv_destination, json_destination, chart_destination, taxonomy_destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with csv_destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    json_destination.write_text(json.dumps(list(rows), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    counts = failure_taxonomy(rows)
    with taxonomy_destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("failure_type", "count"))
        writer.writeheader()
        writer.writerows(
            {"failure_type": failure_type, "count": count}
            for failure_type, count in counts.items()
        )
    if counts and os.getenv("WM_SKIP_PLOTS") != "1" and "PYTEST_CURRENT_TEST" not in os.environ:
        import matplotlib.pyplot as plt

        figure, axis = plt.subplots(figsize=(8, 4))
        axis.bar(counts.keys(), counts.values(), color="#4c78a8")
        axis.set_ylabel("Count")
        axis.set_title("Recorded mechanical and semantic failure categories")
        axis.tick_params(axis="x", rotation=35)
        figure.tight_layout()
        figure.savefig(chart_destination, dpi=180)
        plt.close(figure)
    elif counts:
        chart_destination.write_bytes(b"")
    return {
        "csv": csv_destination,
        "json": json_destination,
        "chart": chart_destination,
        "taxonomy_csv": taxonomy_destination,
    }


def export_graph_pair(
    reference_graph: str | Path,
    generated_graph: str | Path,
    output_path: str | Path,
    *,
    title: str,
) -> Path:
    """Place a declared reference graph beside its rolled-out generated graph."""
    import matplotlib.image as image
    import matplotlib.pyplot as plt

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    for axis, source, label in zip(
        axes, (reference_graph, generated_graph), ("Reference fixture", "LLM-generated rollout")
    ):
        axis.imshow(image.imread(source))
        axis.set_title(label)
        axis.axis("off")
    figure.suptitle(title)
    figure.tight_layout()
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return destination
