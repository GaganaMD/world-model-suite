"""Evaluate the targeted failed-experiment follow-up run."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from src.evaluation import evaluate_world_model

RUN_DIR = REPO_ROOT / "experiments" / "openrouter_game_study" / "failed-followup-20260830"
REFERENCES = json.loads((REPO_ROOT / "json_generation" / "reference_models.json").read_text(encoding="utf-8"))


def main() -> None:
    candidates = sorted((RUN_DIR / "04_world_models").glob("*/world_model.json"))
    if len(candidates) != 10:
        raise RuntimeError(f"Expected 10 targeted follow-up models, found {len(candidates)}")
    rows = []
    for candidate in candidates:
        tag = candidate.parent.name
        case = next(f"G{i}" for i in range(1, 10) if f"_G{i}_" in tag)
        report = evaluate_world_model(
            candidate,
            REFERENCES.get(case.replace("G", "G.")),
            save_pth=True,
            output_dir=str(RUN_DIR / "05_evaluation" / tag),
        )
        rows.append({
            "tag": tag, "case": case, "lane1_passed": report["lane1"]["passed"],
            "lane2_combined_score": report["lane2"]["combined_score"],
            "lane2_skipped": report["lane2"]["details"].get("skipped", False),
            "lane3_checklist_passed": report["lane3"]["checklist_passed"],
            "overall_passed": report["overall_passed"],
            "saved_artifact_count": len(report["saved_artifacts"]),
            "errors": report["lane1"]["errors"],
        })
    summary = {
        "evaluated": len(rows), "lane1_passed": sum(r["lane1_passed"] for r in rows),
        "lane3_passed": sum(r["lane3_checklist_passed"] for r in rows),
        "overall_passed": sum(r["overall_passed"] for r in rows),
        "evaluation_pth_artifacts": sum(r["saved_artifact_count"] for r in rows),
        "records": rows,
    }
    (RUN_DIR / "05_evaluation" / "evaluation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
