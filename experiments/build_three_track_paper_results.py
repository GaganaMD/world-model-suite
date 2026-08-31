"""Build paper summaries for the preserved game, situational, and cultural tracks."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "experiments" / "three_track_paper_results.json"
OUT_FIG = ROOT / "overleaf" / "World Models Workshop" / "fig" / "three_track_summary.pdf"


def game_summary() -> dict:
    path = ROOT / "experiments" / "openrouter_game_study" / "reliability_summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "scope": "G1-G9, five models, three runs",
        "n": data["aggregate"]["first_pass_total"],
        "mechanical_pass": data["aggregate"]["first_pass_passed"],
        "by_model": {x["model"]: x for x in data["by_model"]},
        "source": "experiments/openrouter_game_study/reliability_summary.json",
    }


def situational_summary() -> dict:
    path = ROOT / "notebooks" / "Copy_of_world_models_python_prompting_situational.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    output = "\n".join(
        str(line)
        for cell in notebook["cells"]
        for item in cell.get("outputs", [])
        for line in item.get("text", [])
    )
    pattern = re.compile(
        r"\[\s*(\d+)/165\]\s+(S(\d+)_[^\s]+_g\d+_r0)\s+"
        r"code=([yn]).*?exec=([yn])\s+val=([yn])\s+mech=(PASS|FAIL|INCOMPLETE)"
    )
    rows = [m.groups() for m in pattern.finditer(output) if int(m.group(3)) <= 9]
    if len(rows) != 135:
        raise RuntimeError(f"Expected 135 logged S1-S9 first passes, found {len(rows)}")
    grouped: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for row in rows:
        model = re.search(r"^S\d+_(.+?)_v2_python", row[1]).group(1)
        grouped[model].append(row)
    return {
        "scope": "S1-S9, five models, three generations",
        "n": len(rows),
        "mechanical_pass": sum(r[6] == "PASS" for r in rows),
        "execution_ok": sum(r[4] == "y" for r in rows),
        "validation_ok": sum(r[5] == "y" for r in rows),
        "by_model": {
            model: {"n": len(items), "mechanical_pass": sum(r[6] == "PASS" for r in items)}
            for model, items in sorted(grouped.items())
        },
        "status": dict(Counter(r[6] for r in rows)),
        "source": "saved outputs in notebooks/Copy_of_world_models_python_prompting_situational.ipynb",
        "exclusion": "S10-S11 excluded because the saved execution log is incomplete",
    }


def cultural_summary() -> dict:
    path = ROOT / "report" / "raw_output" / "analysis" / "aggregates.json"
    runs = json.loads(path.read_text(encoding="utf-8"))["runs"]
    return {
        "scope": "C1-C14, three models, anonymized/with-location, one sample per cell",
        "n": sum(x["n"] for x in runs.values()),
        "strict_parse": sum(x["strict_parse"] for x in runs.values()),
        "parse_failed": sum(x["parse_failed"] for x in runs.values()),
        "lane1_pass": sum(x["lane1_pass"] for x in runs.values()),
        "runs": runs,
        "source": "report/raw_output/analysis/aggregates.json",
        "caveat": "automated semantic and bias outputs are diagnostic, not human validated",
    }


def main() -> None:
    result = {"game": game_summary(), "situational": situational_summary(), "cultural": cultural_summary()}
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    names = ["Game", "Situational\n(S1-S9)", "Cultural"]
    passed = [result["game"]["mechanical_pass"], result["situational"]["mechanical_pass"], result["cultural"]["lane1_pass"]]
    totals = [result["game"]["n"], result["situational"]["n"], result["cultural"]["n"]]
    rates = [p / n for p, n in zip(passed, totals)]
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    bars = ax.bar(names, rates, color=["#4477AA", "#EE6677", "#228833"])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Mechanical / Lane-1 pass rate")
    ax.grid(axis="y", alpha=.25)
    for bar, p, n in zip(bars, passed, totals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + .02, f"{p}/{n}", ha="center")
    fig.tight_layout()
    fig.savefig(OUT_FIG)
    plt.close(fig)
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_FIG}")


if __name__ == "__main__":
    main()
