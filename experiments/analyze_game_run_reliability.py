"""Aggregate first-pass and repair-assisted reliability across game POSG runs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "experiments" / "openrouter_game_study"
RUNS = ("run_1", "run_2", "run_3")


def percentage(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 2) if denominator else 0.0


def main() -> None:
    attempts: list[dict] = []
    artifact_audit = []
    for run in RUNS:
        run_dir = ROOT / run
        records = [
            json.loads(line)
            for line in (run_dir / "00_run_info" / "records.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for record in records:
            record["run"] = run
        attempts.extend(records)
        artifact_audit.append(
            {
                "run": run,
                "json_artifacts": len(list((run_dir / "04_world_models").glob("*/world_model.json"))),
                "pth_artifacts": len(list((run_dir / "04_world_models").glob("*/*.pth"))),
            }
        )

    first = [row for row in attempts if row["repair_round"] == 0]
    final: dict[tuple[str, str, str, int], dict] = {}
    for row in attempts:
        final[(row["run"], row["model"], row["case"], row["sample"])] = row

    run_rows = []
    for run in RUNS:
        run_first = [row for row in first if row["run"] == run]
        run_final = [row for key, row in final.items() if key[0] == run]
        audit = next(row for row in artifact_audit if row["run"] == run)
        run_rows.append(
            {
                "run": run,
                "first_pass_passed": sum(row["status"] == "passed" for row in run_first),
                "first_pass_total": len(run_first),
                "first_pass_rate_pct": percentage(sum(row["status"] == "passed" for row in run_first), len(run_first)),
                "final_passed": sum(row["status"] == "passed" for row in run_final),
                "final_total": len(run_final),
                "final_rate_pct": percentage(sum(row["status"] == "passed" for row in run_final), len(run_final)),
                "attempt_count": len([row for row in attempts if row["run"] == run]),
                **audit,
            }
        )

    by_model: dict[str, list[dict]] = defaultdict(list)
    by_cell: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in first:
        by_model[row["model"]].append(row)
        by_cell[(row["model"], row["case"])].append(row)

    model_rows = []
    for model, rows in sorted(by_model.items()):
        passed = sum(row["status"] == "passed" for row in rows)
        model_rows.append(
            {"model": model, "first_pass_passed": passed, "trials": len(rows), "first_pass_rate_pct": percentage(passed, len(rows))}
        )

    cell_rows = []
    for (model, case), rows in sorted(by_cell.items()):
        passed = sum(row["status"] == "passed" for row in rows)
        cell_rows.append(
            {"model": model, "case": case, "first_pass_passed": passed, "trials": len(rows), "first_pass_rate_pct": percentage(passed, len(rows))}
        )

    first_passed = sum(row["status"] == "passed" for row in first)
    final_passed = sum(row["status"] == "passed" for row in final.values())
    report = {
        "runs": run_rows,
        "aggregate": {
            "first_pass_passed": first_passed,
            "first_pass_total": len(first),
            "first_pass_rate_pct": percentage(first_passed, len(first)),
            "final_passed": final_passed,
            "final_total": len(final),
            "final_rate_pct": percentage(final_passed, len(final)),
            "json_artifacts": sum(row["json_artifacts"] for row in artifact_audit),
            "pth_artifacts": sum(row["pth_artifacts"] for row in artifact_audit),
        },
        "by_model": model_rows,
        "by_model_game": cell_rows,
    }
    (ROOT / "reliability_summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for filename, rows in (("reliability_by_run.csv", run_rows), ("reliability_by_model.csv", model_rows), ("reliability_by_model_game.csv", cell_rows)):
        with (ROOT / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    run_table = "\n".join(
        f"| {row['run']} | {row['first_pass_passed']}/{row['first_pass_total']} ({row['first_pass_rate_pct']:.2f}%) | "
        f"{row['final_passed']}/{row['final_total']} ({row['final_rate_pct']:.2f}%) | {row['attempt_count']} | "
        f"{row['json_artifacts']} | {row['pth_artifacts']} |"
        for row in run_rows
    )
    model_table = "\n".join(
        f"| {row['model']} | {row['first_pass_passed']}/{row['trials']} | {row['first_pass_rate_pct']:.2f}% |"
        for row in model_rows
    )
    aggregate = report["aggregate"]
    markdown = f"""# Three-Run Game POSG Reliability

First-pass rate measures unaided generation reliability. Final rate includes explicitly
recorded mechanical repair rounds and measures whether the pipeline eventually produced
a usable contract-valid artifact. Neither metric is a semantic-quality score.

## By Run

| Run | First-pass valid | Final valid | Attempts | JSON | PTH |
| :--- | ---: | ---: | ---: | ---: | ---: |
{run_table}

## Aggregate

- First-pass: {aggregate['first_pass_passed']}/{aggregate['first_pass_total']} ({aggregate['first_pass_rate_pct']:.2f}%)
- Repair-assisted final: {aggregate['final_passed']}/{aggregate['final_total']} ({aggregate['final_rate_pct']:.2f}%)
- Stored artifacts: {aggregate['json_artifacts']} JSON and {aggregate['pth_artifacts']} PTH

## First-Pass Reliability by Model

| Model | Passed/trials | Rate |
| :--- | ---: | ---: |
{model_table}

See `reliability_by_model_game.csv` for the 3-trial result of every model/game pair.
"""
    (ROOT / "RELIABILITY_REPORT.md").write_text(markdown, encoding="utf-8")
    print(json.dumps(report["aggregate"], indent=2))


if __name__ == "__main__":
    main()
