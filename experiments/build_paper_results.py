"""Regenerate paper-facing game-study summaries from preserved artifacts only."""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments" / "openrouter_game_study"
OUT = STUDY / "paper_results.json"


def main() -> None:
    with (STUDY / "evaluation_summary.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    reliability = json.loads((STUDY / "reliability_summary.json").read_text(encoding="utf-8"))

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["model"]].append(row)

    by_model = []
    for model, model_rows in sorted(grouped.items()):
        scores = [float(r["lane2_combined_score"]) for r in model_rows]
        by_model.append({
            "model": model,
            "n": len(model_rows),
            "lane1_passed": sum(r["lane1_passed"] == "True" for r in model_rows),
            "mean_coverage": statistics.mean(float(r["lane2_coverage"]) for r in model_rows),
            "mean_precision": statistics.mean(float(r["lane2_precision"]) for r in model_rows),
            "mean_combined_score": statistics.mean(scores),
            "sd_combined_score": statistics.stdev(scores),
            "exact_combined_matches": sum(score == 1.0 for score in scores),
        })

    passing = [r for r in rows if r["lane1_passed"] == "True"]
    output = {
        "source": "experiments/openrouter_game_study/evaluation_summary.csv",
        "structural_backend": sorted({r["lane2_backend"] for r in rows}),
        "n_evaluated": len(rows),
        "by_model": by_model,
        "conditional_on_lane1_pass": {
            "n": len(passing),
            "mean_combined_score": statistics.mean(
                float(r["lane2_combined_score"]) for r in passing
            ),
            "exact_combined_matches": sum(
                float(r["lane2_combined_score"]) == 1.0 for r in passing
            ),
        },
        "reliability": reliability,
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    labels = [r["model"].replace("_", " ") for r in by_model]
    validity = [
        next(x["first_pass_rate_pct"] for x in reliability["by_model"] if x["model"] == r["model"]) / 100
        for r in by_model
    ]
    structural = [r["mean_combined_score"] for r in by_model]
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.bar([i - 0.19 for i in x], validity, width=0.38, label="First-pass validity")
    ax.bar([i + 0.19 for i in x], structural, width=0.38, label="Fallback structural F1")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Rate / mean score")
    ax.set_xticks(list(x), labels, rotation=18, ha="right")
    ax.legend(frameon=False, ncol=2)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    figure_path = ROOT / "overleaf" / "figures" / "main_empirical_results.pdf"
    fig.savefig(figure_path)
    plt.close(fig)
    print(f"wrote {OUT}")
    print(f"wrote {figure_path}")


if __name__ == "__main__":
    main()
