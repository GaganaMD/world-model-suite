"""Evaluate every final world model in run_1, run_2, and run_3."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.evaluation import evaluate_world_model


ROOT = REPO_ROOT / "experiments" / "openrouter_game_study"
RUNS = ("run_1", "run_2", "run_3")
REFERENCE_PATH = REPO_ROOT / "json_generation" / "reference_models.json"


def compact_row(run: str, tag: str, report: dict[str, Any], reference_used: bool) -> dict[str, Any]:
    model, remainder = tag.split("_G", 1)
    # Restore the full model slug by reading from the right, since slugs contain underscores.
    case = "G" + remainder.split("_s", 1)[0]
    model = tag[: tag.index("_" + case)]
    return {
        "run": run,
        "tag": tag,
        "model": model,
        "case": case,
        "lane1_passed": report["lane1"]["passed"],
        "lane1_error_count": len(report["lane1"]["errors"]),
        "lane2_reference_used": reference_used,
        "lane2_coverage": report["lane2"]["coverage"],
        "lane2_precision": report["lane2"]["precision"],
        "lane2_combined_score": report["lane2"]["combined_score"],
        "lane2_backend": report["lane2"]["details"].get("backend"),
        "lane2_skipped": bool(report["lane2"]["details"].get("skipped")),
        "lane3_checklist_passed": report["lane3"]["checklist_passed"],
        "lane3_bias_check_passed": report["lane3"]["details"]["bias_check_passed"],
        "overall_passed": report["overall_passed"],
        "saved_artifact_count": len(report["saved_artifacts"]),
    }


def main() -> None:
    references = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for run in RUNS:
        run_dir = ROOT / run
        candidates = sorted((run_dir / "04_world_models").glob("*/world_model.json"))
        if len(candidates) != 45:
            raise RuntimeError(f"{run}: expected 45 final world models, found {len(candidates)}")
        for index, candidate in enumerate(candidates, start=1):
            tag = candidate.parent.name
            case = next((f"G{i}" for i in range(1, 10) if f"_G{i}_" in tag), None)
            if case is None:
                raise ValueError(f"Cannot determine game case from {tag}")
            reference = references.get(case.replace("G", "G."))
            output_dir = run_dir / "05_evaluation" / tag
            report = evaluate_world_model(
                candidate_model_path=candidate,
                ground_truth_path=reference,
                save_pth=True,
                output_dir=str(output_dir),
            )
            row = compact_row(run, tag, report, reference is not None)
            rows.append(row)
            print(
                f"[{run} {index:02d}/45] {tag}: "
                f"L1={'PASS' if row['lane1_passed'] else 'FAIL'} "
                f"L2={row['lane2_combined_score']:.3f}{'' if reference else ' (skipped)'} "
                f"L3={'PASS' if row['lane3_checklist_passed'] else 'FAIL'}",
                flush=True,
            )

        run_rows = [row for row in rows if row["run"] == run]
        (run_dir / "05_evaluation" / "evaluation_summary.json").write_text(
            json.dumps(run_rows, indent=2) + "\n", encoding="utf-8"
        )
        with (run_dir / "05_evaluation" / "evaluation_summary.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=list(run_rows[0]))
            writer.writeheader()
            writer.writerows(run_rows)

    aggregate = {
        "evaluated_models": len(rows),
        "lane1_passed": sum(row["lane1_passed"] for row in rows),
        "lane2_scored": sum(row["lane2_reference_used"] for row in rows),
        "lane2_skipped_no_reference": sum(row["lane2_skipped"] for row in rows),
        "lane3_checklist_passed": sum(row["lane3_checklist_passed"] for row in rows),
        "overall_passed": sum(row["overall_passed"] for row in rows),
        "evaluation_pth_artifacts": sum(row["saved_artifact_count"] for row in rows),
    }
    document = {"aggregate": aggregate, "records": rows}
    (ROOT / "evaluation_summary.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "evaluation_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    failures = [row for row in rows if not row["lane1_passed"]]
    scored = [row for row in rows if row["lane2_reference_used"]]
    mean_lane2 = sum(row["lane2_combined_score"] for row in scored) / len(scored)
    failure_lines = "\n".join(
        f"- `{row['run']}/{row['tag']}`: see its `evaluation_report.json` for Lane 1 errors."
        for row in failures
    ) or "- None."
    (ROOT / "EVALUATION_REPORT.md").write_text(
        f"""# Three-Run Evaluation Results

## Aggregate

- Evaluated world models: **{aggregate['evaluated_models']}**
- Lane 1 mechanical passes: **{aggregate['lane1_passed']}/{aggregate['evaluated_models']}**
- Lane 3 checklist passes: **{aggregate['lane3_checklist_passed']}/{aggregate['evaluated_models']}**
- Overall passes under available references: **{aggregate['overall_passed']}/{aggregate['evaluated_models']}**
- Evaluation graph artifacts: **{aggregate['evaluation_pth_artifacts']} `.pth` files**

## Lane 2 Scope

The repository contains ground-truth models only for G1 and G2, so Lane 2 scored
**{aggregate['lane2_scored']}** candidates and explicitly skipped **{aggregate['lane2_skipped_no_reference']}**
G3-G9 candidates. The external `game_matching` package is unavailable in this
workspace; scored rows therefore use the pipeline's documented feature-multiset
fallback. Their mean combined score is **{mean_lane2:.4f}** and must not be presented
as an optimal graph-matching score.

## Lane 1 Failures

{failure_lines}

Detailed reports and candidate/ground-truth graph artifacts are stored under each
run's `05_evaluation/<model_game_attempt>/` directory.
""",
        encoding="utf-8",
    )
    print(json.dumps(aggregate, indent=2))


if __name__ == "__main__":
    main()
