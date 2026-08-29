"""Descriptive repeated-generation analysis for persisted Python POSG experiments."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable, Mapping, Sequence

from .eda import WorldModelEDA
from .experiment_aggregation import load_artifact_rollout
from .semantic_oracle import evaluate_g1_artifact


STRUCTURAL_SIGNATURE_FIELDS = (
    "reachable_states",
    "terminal_states",
    "edges",
    "max_depth",
    "deterministic_fraction",
)


def structural_signature(record: Mapping[str, Any]) -> tuple[Any, ...] | None:
    """Return a stable, intentionally simple signature for successful rollouts."""
    if record.get("rollout_status") != "success" and record.get("status") != "success":
        return None
    values = tuple(record.get(field) for field in STRUCTURAL_SIGNATURE_FIELDS)
    return values if all(value is not None for value in values) else None


def enrich_records(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Add graph descriptors and artifact-presence flags without mutating source records."""
    enriched: list[dict[str, Any]] = []
    for source in records:
        record = dict(source)
        artifact_dir = Path(record["artifact_dir"]) if record.get("artifact_dir") else None
        world_model = artifact_dir / "world_model.json" if artifact_dir else None
        graph = artifact_dir / "graph.png" if artifact_dir else None
        record["world_model_available"] = bool(world_model and world_model.is_file())
        record["graph_available"] = bool(graph and graph.is_file())
        source = artifact_dir / "generated.py" if artifact_dir else None
        if record.get("case") == "G1" and source and source.is_file():
            semantic = evaluate_g1_artifact(source)
            record["semantic_validity"] = semantic["semantic_validity"]
            record["semantic_score"] = semantic["semantic_score"]
            record["semantic_reward_status"] = semantic.get("checks", {}).get("rewards", {}).get("status")
            record["semantic_observation_status"] = semantic.get("checks", {}).get("observations", {}).get("status")
        if record["world_model_available"]:
            rollout = load_artifact_rollout(world_model)
            record["max_depth"] = record.get("max_depth") or max(
                (state["depth"] for state in rollout["states"].values()), default=None
            )
            eda = WorldModelEDA.from_rollout(rollout)
            summary = eda.summary()
            graph_metrics = summary["graph"]
            centrality = eda.centrality_analysis()
            betweenness = list(centrality["betweenness"].values())
            record.setdefault("reachable_states", summary["states"]["state_count"])
            record.setdefault("terminal_states", summary["states"]["terminal_state_count"])
            record.setdefault("edges", graph_metrics["edge_count"])
            record.setdefault("max_depth", summary["states"]["maximum_trajectory_depth"])
            record.setdefault("avg_branching", summary["states"]["mean_branching_factor"])
            record.setdefault(
                "deterministic_fraction",
                summary["transitions"]["deterministic_transition_fraction"],
            )
            record.setdefault(
                "stochastic_fraction", summary["transitions"]["stochastic_transition_fraction"]
            )
            record.setdefault("avg_entropy", summary["transitions"]["mean_transition_entropy"])
            record.update(
                {
                    "graph_nodes": summary["states"]["state_count"],
                    "graph_edges": graph_metrics["edge_count"],
                    "graph_density": graph_metrics["density"],
                    "average_in_degree": graph_metrics["average_in_degree"],
                    "average_out_degree": graph_metrics["average_out_degree"],
                    "scc_count": graph_metrics["strongly_connected_component_count"],
                    "average_path_length": graph_metrics["average_shortest_path_length"],
                    "global_efficiency": graph_metrics["global_efficiency"],
                    "mean_betweenness": mean(betweenness) if betweenness else None,
                    "max_betweenness": max(betweenness, default=None),
                }
            )
        enriched.append(record)
    return enriched


def _summary(values: Iterable[object]) -> dict[str, float | int | None]:
    numeric = [float(value) for value in values if isinstance(value, (int, float))]
    return {
        "n": len(numeric),
        "mean": mean(numeric) if numeric else None,
        "stddev": pstdev(numeric) if len(numeric) > 1 else 0.0 if numeric else None,
    }


def summarize_variability(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Summarize repeated samples descriptively by model, case, and prompt variant."""
    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[
            (
                str(record.get("model", "")),
                str(record.get("case", "")),
                str(record.get("prompt_variant", "P0")),
            )
        ].append(record)

    summaries = []
    for (model, case, prompt_variant), group in sorted(grouped.items()):
        structurally_valid = [
            record
            for record in group
            if record.get("structural_validation_status") == "success"
            or (
                record.get("status") == "success"
                and record.get("structural_validation_status") in (None, "not_run")
            )
        ]
        signatures = Counter(
            signature
            for record in structurally_valid
            if (signature := structural_signature(record)) is not None
        )
        row: dict[str, Any] = {
            "model": model,
            "case": case,
            "prompt_variant": prompt_variant,
            "attempts": len(group),
            "generation_success_rate": sum(
                record.get("generation_status") == "success" for record in group
            )
            / len(group),
            "structural_validation_success_rate": sum(
                record.get("structural_validation_status") == "success"
                or record.get("status") == "success"
                for record in group
            )
            / len(group),
            "rollout_success_rate": sum(
                record.get("rollout_status") == "success" or record.get("status") == "success"
                for record in group
            )
            / len(group),
            "structurally_valid_samples": len(structurally_valid),
            "same_signature_proportion": max(signatures.values()) / len(structurally_valid)
            if structurally_valid and signatures
            else None,
            "failure_mode_frequencies": dict(
                sorted(Counter(
                    str(record["failure_type"])
                    for record in group
                    if record.get("failure_type")
                ).items())
            ),
        }
        for field in (
            "reachable_states",
            "terminal_states",
            "edges",
            "avg_branching",
            "deterministic_fraction",
            "stochastic_fraction",
            "avg_entropy",
            "max_depth",
        ):
            stats = _summary(record.get(field) for record in structurally_valid)
            row[f"mean_{field}"] = stats["mean"]
            row[f"stddev_{field}"] = stats["stddev"]
        row["max_depth_distribution"] = dict(
            sorted(Counter(str(record.get("max_depth")) for record in structurally_valid).items())
        )
        summaries.append(row)
    return summaries


def reference_deltas(
    records: Iterable[Mapping[str, Any]], reference_metrics: Mapping[str, Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """Attach simple descriptor differences to successful generated records."""
    rows = []
    for source in records:
        record = dict(source)
        reference = reference_metrics.get(str(record.get("case")))
        if record.get("status") == "success" and reference:
            for field in (
                "reachable_states",
                "terminal_states",
                "edges",
                "max_depth",
                "avg_branching",
                "deterministic_fraction",
                "stochastic_fraction",
                "avg_entropy",
            ):
                value, expected = record.get(field), reference.get(field)
                if isinstance(value, (int, float)) and isinstance(expected, (int, float)):
                    record[f"reference_{field}"] = expected
                    record[f"{field}_difference"] = value - expected
        rows.append(record)
    return rows


def export_robustness_report(
    records: Sequence[Mapping[str, Any]], output_dir: str | Path
) -> dict[str, Path]:
    """Write immutable machine-readable rows, descriptive summaries, and one plot."""
    destination = Path(output_dir)
    targets = {
        "records_json": destination / "experiment_rows.json",
        "records_csv": destination / "experiment_rows.csv",
        "summary_json": destination / "variability_summary.json",
        "summary_markdown": destination / "variability_summary.md",
        "plot": destination / "variability.png",
    }
    if any(path.exists() for path in targets.values()):
        raise FileExistsError(f"Refusing to overwrite robustness analysis in {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    rows = enrich_records(records)
    summaries = summarize_variability(rows)
    targets["records_json"].write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = sorted({key for row in rows for key in row})
    with targets["records_csv"].open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    targets["summary_json"].write_text(
        json.dumps(summaries, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_summary_markdown(summaries, rows, targets["summary_markdown"])
    _plot_variability(rows, targets["plot"])
    return targets


def _write_summary_markdown(
    summaries: Sequence[Mapping[str, Any]], records: Sequence[Mapping[str, Any]], path: Path
) -> None:
    lines = [
        "# Repeated-generation robustness summary",
        "",
        "Descriptive statistics only; this report makes no statistical-significance claim.",
        "",
        "| Model | Case | Prompt | Attempts | Structural success | Same signature among structurally valid rollouts | Failures |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in summaries:
        lines.append(
            "| {model} | {case} | {prompt_variant} | {attempts} | {structural_validation_success_rate:.2f} | "
            "{same_signature} | {failures} |".format(
                **row,
                same_signature=(
                    f"{row['same_signature_proportion']:.2f}"
                    if row["same_signature_proportion"] is not None
                    else "N/A"
                ),
                failures=json.dumps(row["failure_mode_frequencies"], sort_keys=True),
            )
        )
    g1_records = [record for record in records if record.get("case") == "G1"]
    if g1_records:
        lines.extend(
            [
                "",
                "## G1 sample comparison",
                "",
                "| Sample | Prompt | Status | States | Terminals | Edges | Max depth | Branching | Entropy | Δ states | Δ terminals | Δ edges |",
                "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in sorted(g1_records, key=lambda record: (str(record.get("prompt_variant")), int(record["sample"]))):
            lines.append(
                "| {sample} | {prompt_variant} | {status} | {reachable_states} | {terminal_states} | "
                "{edges} | {max_depth} | {avg_branching} | {avg_entropy} | {reachable_states_difference} | "
                "{terminal_states_difference} | {edges_difference} |".format(
                    **{key: row.get(key, "N/A") for key in (
                        "sample", "prompt_variant", "status", "reachable_states", "terminal_states",
                        "edges", "max_depth", "avg_branching", "avg_entropy",
                        "reachable_states_difference", "terminal_states_difference", "edges_difference",
                    )}
                )
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _plot_variability(records: Sequence[Mapping[str, Any]], path: Path) -> None:
    import matplotlib.pyplot as plt

    successful = [record for record in records if record.get("status") == "success"]
    figure, axis = plt.subplots(figsize=(10, 4))
    labels = [
        f"{record.get('case')}/{record.get('prompt_variant')}/#{record.get('sample')}"
        for record in successful
    ]
    axis.bar(labels, [record.get("reachable_states", 0) for record in successful], color="#4c78a8")
    axis.set_ylabel("Reachable states")
    axis.set_title("Repeated-generation structural variability")
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
