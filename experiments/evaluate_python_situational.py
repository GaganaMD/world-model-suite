"""Evaluate every saved situational Python POSG through the three-lane pipeline.

The generated programs are untrusted, so they are first executed by the existing
``python_prompting.probe_runner`` subprocess.  Complete rollouts are converted to v2
JSON and evaluated against the explicitly provisional S1--S11 references.  Results
retain repair-round metadata; no attempt is silently replaced by a later repair.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate_mechanical, evaluate_qualitative, evaluate_structural


DEFAULT_INPUT = ROOT / "results" / "python-situational" / "generated_python"
DEFAULT_REFERENCES = ROOT / "data" / "reference_models" / "situational_provisional_v2.json"
DEFAULT_OUTPUT = ROOT / "results" / "python-situational" / "evaluation"
NAME = re.compile(
    r"^(S\d+)_(.+)_v2_python_g(\d+)_r(\d+)\.py$"
)


def probe(path: Path, timeout: int) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "python_prompting.probe_runner",
        str(ROOT),
        str(path),
        "{}",
    ]
    try:
        completed = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "errors": [f"probe exceeded {timeout}s"], "v2": None}
    if completed.returncode or not completed.stdout.strip():
        detail = completed.stderr.strip() or f"probe exited {completed.returncode}"
        return {"status": "FAIL", "errors": [detail], "v2": None}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        return {"status": "FAIL", "errors": [f"invalid probe JSON: {error}"], "v2": None}


def evaluate_one(path: Path, references: dict[str, Any], timeout: int) -> dict[str, Any]:
    match = NAME.match(path.name)
    if not match:
        raise ValueError(f"unexpected generated filename: {path.name}")
    case, model, generation, repair = match.groups()
    result = probe(path, timeout)
    row: dict[str, Any] = {
        "file": path.name,
        "case": case,
        "model": model,
        "generation": int(generation),
        "repair_round": int(repair),
        "is_first_pass": repair == "0",
        "probe_status": result.get("status", "FAIL"),
        "probe_errors": result.get("errors", []),
        "jobst_validate_passed": bool((result.get("jobst_validate") or {}).get("passed")),
        "lane1_passed": False,
        "lane1_errors": [],
        "lane2_coverage": None,
        "lane2_precision": None,
        "lane2_combined_score": None,
        "lane2_backend": None,
        "lane3_checklist_passed": False,
        "lane3_bias_check_passed": False,
        "lane3_bias_flags": [],
    }
    candidate = result.get("v2")
    if candidate is None:
        return row
    lane1 = evaluate_mechanical(candidate)
    lane2 = evaluate_structural(candidate, references[case])
    lane3 = evaluate_qualitative(candidate, references[case])
    row.update(
        lane1_passed=lane1["passed"],
        lane1_errors=lane1["errors"],
        lane2_coverage=lane2["coverage"],
        lane2_precision=lane2["precision"],
        lane2_combined_score=lane2["combined_score"],
        lane2_backend=lane2["details"].get("backend"),
        lane3_checklist_passed=lane3["checklist_passed"],
        lane3_bias_check_passed=lane3["details"]["bias_check_passed"],
        lane3_bias_flags=lane3["details"]["bias_flags"],
    )
    return row


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups["all"].append(row)
        groups["first_pass" if row["is_first_pass"] else "repair"].append(row)

    def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
        scored = [row for row in items if row["lane2_combined_score"] is not None]
        return {
            "attempts": len(items),
            "probe_passed": sum(row["probe_status"] == "PASS" for row in items),
            "lane1_passed": sum(row["lane1_passed"] for row in items),
            "lane2_scored": len(scored),
            "lane2_mean_coverage": (
                sum(row["lane2_coverage"] for row in scored) / len(scored) if scored else None
            ),
            "lane2_mean_precision": (
                sum(row["lane2_precision"] for row in scored) / len(scored) if scored else None
            ),
            "lane2_mean_combined_score": (
                sum(row["lane2_combined_score"] for row in scored) / len(scored) if scored else None
            ),
            "lane3_checklist_passed": sum(row["lane3_checklist_passed"] for row in items),
            "lane3_bias_check_passed": sum(row["lane3_bias_check_passed"] for row in items),
            "probe_statuses": dict(Counter(row["probe_status"] for row in items)),
        }

    return {name: summarize(items) for name, items in groups.items()}


def grouped_rows(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    output = []
    for value in sorted({row[field] for row in rows}):
        items = [row for row in rows if row[field] == value]
        scores = [row for row in items if row["lane2_combined_score"] is not None]
        output.append(
            {
                field: value,
                "attempts": len(items),
                "probe_passed": sum(row["probe_status"] == "PASS" for row in items),
                "lane1_passed": sum(row["lane1_passed"] for row in items),
                "lane2_scored": len(scores),
                "lane2_mean_coverage": (
                    sum(row["lane2_coverage"] for row in scores) / len(scores) if scores else None
                ),
                "lane2_mean_precision": (
                    sum(row["lane2_precision"] for row in scores) / len(scores) if scores else None
                ),
                "lane2_mean_combined_score": (
                    sum(row["lane2_combined_score"] for row in scores) / len(scores) if scores else None
                ),
                "lane3_checklist_passed": sum(row["lane3_checklist_passed"] for row in items),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--references", type=Path, default=DEFAULT_REFERENCES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    references = json.loads(args.references.read_text(encoding="utf-8"))
    paths = sorted(args.input_dir.glob("*.py"))
    rows = [evaluate_one(path, references, args.timeout) for path in paths]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "attempt_results.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    csv_rows = [
        {key: json.dumps(value) if isinstance(value, list) else value for key, value in row.items()}
        for row in rows
    ]
    write_csv(args.output_dir / "attempt_results.csv", csv_rows)
    write_csv(args.output_dir / "summary_by_case.csv", grouped_rows(rows, "case"))
    write_csv(args.output_dir / "summary_by_model.csv", grouped_rows(rows, "model"))
    summary = aggregate(rows)
    summary["protocol"] = {
        "input_glob": str(args.input_dir.relative_to(ROOT) / "*.py"),
        "reference_file": str(args.references.relative_to(ROOT)),
        "includes_repair_rounds": True,
        "lane2_reference_status": "provisional; criteria-derived; not independent ground truth",
        "execution": "offline CPU evaluation of repository artifacts; no LLM calls",
        "input_sha256": hashlib.sha256(
            b"".join(path.name.encode() + b"\0" + path.read_bytes() for path in paths)
        ).hexdigest(),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
