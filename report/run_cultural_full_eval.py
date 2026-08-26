"""Run the full cultural evaluation (Lanes 0/1/3 + structural EDA) on all 14
reference world models, against both the case bank with place names and the
`cultural_without_loc` bank.

This mirrors what `evaluate_cultural.py --candidates` does per bank, and compares
the two so we can see whether the *expected level of output* (the authored
reference world model) is preserved when the location labels are stripped.

    python report/run_cultural_full_eval.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluate_cultural import load_cases, evaluate_candidate  # noqa: E402

ORIGINAL = ROOT / "data" / "Test_Cases" / "04_cultural"
WITHOUT_LOC = ROOT / "data" / "Test_Cases" / "cultural_without_loc"
REFERENCES = ROOT / "data" / "Test_Cases" / "04_cultural" / "reference_models.json"
OUT = ROOT / "report" / "cultural_full_eval_comparison.json"


def load_bank(directory: Path):
    return load_cases(cases_dir=directory)


def main() -> int:
    refs = json.loads(REFERENCES.read_text(encoding="utf-8"))["references"]
    cases_original = load_bank(ORIGINAL)
    cases_without = load_bank(WITHOUT_LOC)
    order = [f"C{n}" for n in range(1, 15)]

    rows = []
    for cid in order:
        raw = json.dumps(refs[cid])
        original_case = next(c for c in cases_original if c.cid == cid)
        without_case = next(c for c in cases_without if c.cid == cid)
        r_orig = evaluate_candidate(original_case, raw, {"model": "reference", "sample": "bank"})
        r_wl = evaluate_candidate(without_case, raw, {"model": "reference", "sample": "without_loc"})

        def lane3(rec):
            return rec["lane3"] or {}

        rows.append({
            "case": cid,
            "original": {
                "lane1": r_orig["lane1"]["verdict"] if r_orig["lane1"] else None,
                "coverage": lane3(r_orig).get("coverage"),
                "avoidance": lane3(r_orig).get("avoidance"),
                "lane3": lane3(r_orig).get("lane3"),
                "states": r_orig["eda"]["states"]["state_count"] if r_orig["eda"] else None,
            },
            "without_loc": {
                "lane1": r_wl["lane1"]["verdict"] if r_wl["lane1"] else None,
                "coverage": lane3(r_wl).get("coverage"),
                "avoidance": lane3(r_wl).get("avoidance"),
                "lane3": lane3(r_wl).get("lane3"),
                "states": r_wl["eda"]["states"]["state_count"] if r_wl["eda"] else None,
            },
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    print(f"{'Case':5} {'L1':>4} {'cov':>5} {'avd':>5} {'l3':>5} | {'L1':>4} {'cov':>5} {'avd':>5} {'l3':>5}  without_loc")
    for row in rows:
        o, w = row["original"], row["without_loc"]
        print(
            f"{row['case']:5} {str(o['lane1']):>4} {fmt(o['coverage']):>5} {fmt(o['avoidance']):>5} {fmt(o['lane3']):>5} | "
            f"{str(w['lane1']):>4} {fmt(w['coverage']):>5} {fmt(w['avoidance']):>5} {fmt(w['lane3']):>5}"
        )
    print(f"\nwrote {OUT}")
    return 0


def fmt(value):
    return "   -" if value is None else f"{value:.2f}"


if __name__ == "__main__":
    raise SystemExit(main())