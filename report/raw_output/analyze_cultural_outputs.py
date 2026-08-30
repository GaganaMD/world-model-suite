#!/usr/bin/env python3
"""Three-lane evaluation of the raw cultural-track LLM transcripts.

Reads the six raw transcripts in ``report/raw_output`` (3 models x 2 prompt
conditions x 14 cases = 84 candidates) and runs every candidate through the
repository's modular pipeline ``src/evaluation``:

  - Lane 0 (parse report): strict JSON parse of the block exactly as it came
    back, plus a lenient recovery (fence unwrap / brace substring) so model
    quality is still scored when only the packaging is wrong;
  - Lane 1: ``evaluate_mechanical`` — schema, probability, action-profile and
    reachability checks (tolerance 1e-3);
  - Lane 2: ``evaluate_structural`` against the case's authored reference model
    (v1 -> v2 via ``evaluate_cultural.to_v2``). The external ``game_matching``
    package is unavailable in this workspace, so Lane 2 runs the pipeline's
    documented ``feature_multiset_fallback`` backend (name-insensitive feature
    overlap, not optimal graph matching);
  - Lane 3: ``evaluate_qualitative`` — stakeholder/state/consequence checklist
    plus the bias scan.

On top of the pipeline, two study-specific metrics are added:

  - **Semantic lane** — the case bank's expect/avoid ingredient scoring from
    ``evaluate_cultural.eval_lane3`` (coverage of expected ingredients with
    evidence, flags on forbidden content, geometric-mean score);
  - **Self-consistency F1** — feature-multiset F1 between a model's own two
    versions of the same case (country anonymized vs. country revealed),
    via ``evaluate_structural``.

Outputs (under ``report/raw_output/``):

  analysis/cultural_pipeline_results.json    full per-candidate records
  analysis/aggregates.json                   per-run / per-case aggregates
  analysis/evaluation_results/<run>/<case>/evaluation_report.json
                                             the pipeline's own artifacts
  README.md                                  the analysis report

    python report/raw_output/analyze_cultural_outputs.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate_world_model  # noqa: E402
from src.evaluation.lane2_structural import evaluate_structural  # noqa: E402
import evaluate_cultural as ec  # noqa: E402

RAW_DIR = ROOT / "report" / "raw_output"
ANALYSIS_DIR = RAW_DIR / "analysis"
RESULTS_DIR = ANALYSIS_DIR / "evaluation_results"
REFERENCES = ROOT / "data" / "Test_Cases" / "04_cultural" / "reference_models.json"
BANK_ORIGINAL = ROOT / "data" / "Test_Cases" / "04_cultural"
BANK_WITHOUT_LOC = ROOT / "data" / "Test_Cases" / "cultural_without_loc"

MODELS = ["gpt5-6sol", "llama3-3", "opus5"]
CONDITIONS = ["anonymized", "with_location"]  # anonymized == "Location" label
CASE_IDS = [f"C{n}" for n in range(1, 15)]

TRANSCRIPTS = {
    ("gpt5-6sol", "anonymized"): "cultural_gpt5-6sol_output.txt",
    ("gpt5-6sol", "with_location"): "cultural_gpt5-6sol_output_w_loc.txt",
    ("llama3-3", "anonymized"): "cultural_llama3-3_output.txt",
    ("llama3-3", "with_location"): "cultural_llama3-3_output_w_loc.txt",
    ("opus5", "anonymized"): "cultural_opus5_output.txt",
    ("opus5", "with_location"): "cultural_opus5_output_w_loc.txt",
}

BLOCK_RE = re.compile(r"^=====\s*C(\d+)\s*\(([^)]*)\)\s*[—-]\s*(.+?)\s*=====\s*$", re.M)
FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)

# --------------------------------------------------------------------------- #
# Transcript parsing                                                            #
# --------------------------------------------------------------------------- #

def parse_transcript(path: Path):
    """-> (header dict, [block dict]) for one raw transcript.

    Layout: line 1 is ``provider: ... | cases: 14 | system: ...``; then one
    ``===== C<n> (<label>) — <title> =====`` header per case followed by the
    candidate's raw reply (JSON, sometimes fenced).
    """
    text = path.read_text(encoding="utf-8")
    header_line, _, _ = text.partition("\n")
    header = {}
    for part in header_line.split("|"):
        if ": " in part:
            key, value = part.strip().split(": ", 1)
            header["provider" if key == "initial provider" else key] = value
    blocks = []
    matches = list(BLOCK_RE.finditer(text))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks.append({
            "case": f"C{int(match.group(1))}",
            "label": match.group(2).strip(),
            "title": match.group(3).strip(),
            "raw": text[start:end].strip(),
        })
    return header, blocks


def extract_json(raw: str):
    """Recover one JSON object from a reply block.

    Returns (model | None, method) with method one of
    ``strict`` (parsed as-is), ``fence`` (single ``` block), ``brace``
    (first '{' .. last '}'), or ``failed``.
    """
    try:
        return json.loads(raw), "strict"
    except json.JSONDecodeError:
        pass
    for fence in FENCE_RE.findall(raw):
        try:
            return json.loads(fence.strip()), "fence"
        except json.JSONDecodeError:
            continue
    if "{" in raw and "}" in raw:
        try:
            return json.loads(raw[raw.find("{"): raw.rfind("}") + 1]), "brace"
        except json.JSONDecodeError:
            pass
    return None, "failed"

# --------------------------------------------------------------------------- #
# Per-candidate evaluation                                                      #
# --------------------------------------------------------------------------- #

def lane1_summary(lane1: dict) -> dict:
    findings = lane1["details"]["findings"]
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    return {
        "passed": bool(lane1["passed"]),
        "n_errors": len(errors),
        "n_warnings": len(warnings),
        "errors": [{"rule": f["check"], "message": f["message"]} for f in errors],
        "warning_rules": sorted({f["check"] for f in warnings}),
        "state_count": lane1["details"]["state_count"],
        "reachable_states": len(lane1["details"]["reachable_states"]),
        "states_with_terminal_path": len(lane1["details"]["states_with_terminal_path"]),
    }


def evaluate_candidate(run: tuple, block: dict, case_obj, ref_v2: dict) -> dict:
    """Lane 0 report + the src/evaluation three lanes + the semantic lane."""
    model_name, condition = run
    model, method = extract_json(block["raw"])
    record = {
        "model": model_name,
        "condition": condition,
        "case": block["case"],
        "country": case_obj.country,
        "block_label": block["label"],
        "parse": {"method": method, "strict_pass": method == "strict"},
        "lane1": None,
        "lane2": None,
        "lane3": None,
        "semantic": None,
        "self_consistency_f1": None,
        "overall_passed": None,
    }
    if model is None:
        tail = re.sub(r"\s+", " ", block["raw"][-60:])
        record["parse"]["error"] = (
            "no JSON object could be recovered; the reply is truncated mid-structure "
            f"and ends with: ...{tail!r}")
        return record
    try:
        v2, schema = ec.to_v2(json.loads(json.dumps(model)))
    except ec.ConvertError as exc:
        record["parse"]["schema_error"] = str(exc)
        return record
    record["parse"]["schema"] = schema
    record["_v2"] = v2  # stripped before serialization

    out_dir = RESULTS_DIR / f"{model_name}__{condition}" / block["case"]
    report = evaluate_world_model(
        candidate_model_path=v2,
        ground_truth_path=ref_v2,
        save_pth=False,
        output_dir=str(out_dir),
    )
    record["lane1"] = lane1_summary(report["lane1"])
    record["lane2"] = {
        "coverage": report["lane2"]["coverage"],
        "precision": report["lane2"]["precision"],
        "combined": report["lane2"]["combined_score"],
        "backend": report["lane2"]["details"].get("backend"),
        "skipped": bool(report["lane2"]["details"].get("skipped")),
    }
    details = report["lane3"]["details"]
    record["lane3"] = {
        "checklist_passed": report["lane3"]["checklist_passed"],
        "checklist": details["checklist"],
        "bias_flags": details["bias_flags"],
        "bias_check_passed": details["bias_check_passed"],
        "action_disparity": details["maximum_action_count_disparity"],
        "stakeholder_coverage": details["stakeholder_coverage"],
    }
    try:
        record["semantic"] = semantic_summary(case_obj, v2, model)
    except Exception as exc:  # the semantic lane must not kill the batch
        record["semantic"] = {"error": f"{type(exc).__name__}: {exc}"}
    record["overall_passed"] = bool(report["overall_passed"])
    return record

# --------------------------------------------------------------------------- #
# Semantic lane + data loading                                                  #
# --------------------------------------------------------------------------- #

def semantic_summary(case_obj, v2: dict, model: dict) -> dict:
    """Case-bank expect/avoid scoring (evaluate_cultural's semantic Lane 3)."""
    sem = ec.eval_lane3(case_obj, v2, ec.flatten_text(model))
    return {
        "n_expected": sem["n_expected"],
        "n_covered": sem["n_covered"],
        "n_partial": sem["n_partial"],
        "n_forbidden": sem["n_forbidden"],
        "n_flagged_bullets": sem["n_flagged_bullets"],
        "coverage": sem["coverage"],
        "avoidance": sem["avoidance"],
        "score": sem["lane3"],
        "flags": sorted({f["label"] for f in sem["flags"]}),
        "missing_bullets": [r["bullet"] for r in sem["expected_rows"] if r["status"] == "missing"],
        "partial_bullets": [r["bullet"] for r in sem["expected_rows"] if r["status"] == "partial"],
    }


def load_bank_cases():
    """Parse both case banks; assert the criteria bullets are identical."""
    original = {c.cid: c for c in ec.load_cases(cases_dir=BANK_ORIGINAL)}
    without = {c.cid: c for c in ec.load_cases(cases_dir=BANK_WITHOUT_LOC)}
    mismatches = []
    for cid in CASE_IDS:
        for side in ("expected", "forbidden"):
            a = [x.clean for x in getattr(original[cid], side)]
            b = [x.clean for x in getattr(without[cid], side)]
            if a != b:
                mismatches.append(f"{cid}.{side}")
    return original, without, mismatches


def load_references():
    """Authored reference models (v1 schema) -> v2 for the evaluation lanes."""
    payload = json.loads(REFERENCES.read_text(encoding="utf-8"))
    refs_v2 = {}
    for cid, model in payload["references"].items():
        v2, _ = ec.to_v2(json.loads(json.dumps(model)))
        refs_v2[cid] = v2
    return payload["references"], refs_v2

# --------------------------------------------------------------------------- #
# Batch driver                                                                  #
# --------------------------------------------------------------------------- #

def run_batch():
    original_bank, without_bank, mismatches = load_bank_cases()
    raw_refs, refs_v2 = load_references()
    records = []
    for run, fname in TRANSCRIPTS.items():
        header, blocks = parse_transcript(RAW_DIR / fname)
        if len(blocks) != len(CASE_IDS):
            print(f"  [warn] {fname}: {len(blocks)} case blocks (expected 14)")
        case_bank = original_bank if run[1] == "with_location" else without_bank
        for block in blocks:
            case_obj = case_bank[block["case"]]
            record = evaluate_candidate(run, block, case_obj, refs_v2[block["case"]])
            # The Country column always shows the true country; in the anonymized
            # condition the model itself only saw the "Location" label.
            record["country"] = original_bank[block["case"]].country
            record["transcript"] = fname
            record["provider"] = header.get("provider", "")
            records.append(record)

    # Cross-condition self-consistency: F1 between a model's two versions of
    # the same case (anonymized vs. with_location), via the same structural
    # scorer used by Lane 2.
    by_key = {(r["model"], r["condition"], r["case"]): r for r in records}
    for model in MODELS:
        for cid in CASE_IDS:
            anon = by_key.get((model, "anonymized", cid))
            wloc = by_key.get((model, "with_location", cid))
            if not (anon and wloc):
                continue
            if anon["parse"].get("schema") is None or wloc["parse"].get("schema") is None:
                continue
            score = evaluate_structural(wloc["_v2"], anon["_v2"])
            f1 = score["combined_score"]
            anon["self_consistency_f1"] = f1
            wloc["self_consistency_f1"] = f1
    for record in records:
        record.pop("_v2", None)  # the live models are not JSON-serializable payload
    return records, raw_refs, mismatches

# --------------------------------------------------------------------------- #
# Aggregation                                                                   #
# --------------------------------------------------------------------------- #

def mean(values):
    vals = [v for v in values if isinstance(v, (int, float))]
    return sum(vals) / len(vals) if vals else None


def aggregate(records, refs_v2):
    """Per-run, per-case and per-model aggregates for the report."""
    agg = {"runs": {}, "cases": {}, "models": {}, "rules": []}

    rule_counter, rule_example = Counter(), {}
    for record in records:
        for error in (record["lane1"] or {}).get("errors", []):
            rule_counter[error["rule"]] += 1
            rule_example.setdefault(error["rule"], error["message"])
    agg["rules"] = [
        {"rule": rule, "count": count, "example": rule_example.get(rule, "")}
        for rule, count in rule_counter.most_common()
    ]

    for model in MODELS:
        for condition in CONDITIONS:
            sel = [r for r in records if r["model"] == model and r["condition"] == condition]
            missing, sem_flags, bias_flags = Counter(), Counter(), Counter()
            for r in sel:
                for bullet in (r["semantic"] or {}).get("missing_bullets", []):
                    missing[bullet] += 1
                for label in (r["semantic"] or {}).get("flags", []):
                    sem_flags[label] += 1
                for flag in (r["lane3"] or {}).get("bias_flags", []):
                    label = flag.split(":")[0]
                    if label.startswith("action-profile representation"):
                        # the per-candidate disparity number stays in the records
                        label = "action-profile representation differs across players (disparity)"
                    bias_flags[label[:90]] += 1
            agg["runs"][f"{model}__{condition}"] = {
                "n": len(sel),
                "strict_parse": sum(1 for r in sel if r["parse"]["strict_pass"]),
                "recovered": sum(1 for r in sel if r["parse"]["method"] in ("fence", "brace")),
                "parse_failed": sum(1 for r in sel if r["parse"]["method"] == "failed"),
                "lane1_pass": sum(1 for r in sel if r["lane1"] and r["lane1"]["passed"]),
                "overall_pass": sum(1 for r in sel if r["overall_passed"]),
                "lane3_checklist_pass": sum(1 for r in sel if r["lane3"] and r["lane3"]["checklist_passed"]),
                "bias_free": sum(1 for r in sel if r["lane3"] and r["lane3"]["bias_check_passed"]),
                "mean_lane2_coverage": mean(r["lane2"]["coverage"] for r in sel if r["lane2"]),
                "mean_lane2_precision": mean(r["lane2"]["precision"] for r in sel if r["lane2"]),
                "mean_lane2_combined": mean(r["lane2"]["combined"] for r in sel if r["lane2"]),
                "mean_sem_coverage": mean((r["semantic"] or {}).get("coverage") for r in sel),
                "mean_sem_avoidance": mean((r["semantic"] or {}).get("avoidance") for r in sel),
                "mean_sem_score": mean((r["semantic"] or {}).get("score") for r in sel),
                "mean_states": mean((r["lane1"] or {}).get("state_count") for r in sel),
                "mean_stakeholder_coverage": mean((r["lane3"] or {}).get("stakeholder_coverage") for r in sel),
                "mean_self_consistency": mean(r["self_consistency_f1"] for r in sel),
                "top_missing": missing.most_common(6),
                "semantic_flags": sem_flags.most_common(),
                "bias_flags": bias_flags.most_common(),
            }

    for model in MODELS:
        sel = [r for r in records if r["model"] == model]
        anon = [r for r in sel if r["condition"] == "anonymized"]
        wloc = [r for r in sel if r["condition"] == "with_location"]
        agg["models"][model] = {
            "mean_lane2_combined": mean(r["lane2"]["combined"] for r in sel if r["lane2"]),
            "mean_sem_score": mean((r["semantic"] or {}).get("score") for r in sel),
            "lane1_pass": sum(1 for r in sel if r["lane1"] and r["lane1"]["passed"]),
            "overall_pass": sum(1 for r in sel if r["overall_passed"]),
            "delta_sem": (mean((r["semantic"] or {}).get("score") for r in wloc)
                          - mean((r["semantic"] or {}).get("score") for r in anon)),
            "delta_combined": (mean(r["lane2"]["combined"] for r in wloc if r["lane2"])
                               - mean(r["lane2"]["combined"] for r in anon if r["lane2"])),
            "mean_self_consistency": mean(r["self_consistency_f1"] for r in anon),
        }

    for cid in CASE_IDS:
        sel = [r for r in records if r["case"] == cid]
        ref_states = refs_v2[cid].get("states", [])
        agg["cases"][cid] = {
            "country": sel[0]["country"] if sel else "",
            "ref_states": len(ref_states),
            "ref_terminals": sum(1 for s in ref_states if s.get("terminal")),
            "n_expected": sel[0]["semantic"].get("n_expected") if sel and sel[0]["semantic"] else None,
            "n_forbidden": sel[0]["semantic"].get("n_forbidden") if sel and sel[0]["semantic"] else None,
            "lane1_pass": sum(1 for r in sel if r["lane1"] and r["lane1"]["passed"]),
            "overall_pass": sum(1 for r in sel if r["overall_passed"]),
            "mean_lane2_combined": mean(r["lane2"]["combined"] for r in sel if r["lane2"]),
            "mean_sem_score": mean((r["semantic"] or {}).get("score") for r in sel),
        }
    return agg

# --------------------------------------------------------------------------- #
# README rendering                                                              #
# --------------------------------------------------------------------------- #

def cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def fmt(value, spec=".3f"):
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    return format(value, spec)


def parse_label(method: str) -> str:
    return {"strict": "ok", "fence": "fence", "brace": "brace", "failed": "FAIL"}.get(method, method)


def render_run_table(records, model, condition) -> str:
    """The 14-case metric table for one model x condition run."""
    sel = {r["case"]: r for r in records if r["model"] == model and r["condition"] == condition}
    out = [
        "| Case | Country | Parse | L1 | E/W | States | L2 cov | L2 prec | L2 comb "
        "| L3 chk | Bias | StakeCov | Sem cov | Sem avd | Sem | SelfF1 | Overall |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cid in CASE_IDS:
        r = sel.get(cid)
        if r is None:
            continue
        l1, l2, l3, sem = r["lane1"], r["lane2"], r["lane3"], r["semantic"] or {}
        out.append(
            "| {cid} | {ctry} | {parse} | {l1v} | {ew} | {st} | {cov} | {prec} | {comb} "
            "| {chk} | {bias} | {stake} | {scov} | {savd} | {sem} | {f1} | {overall} |".format(
                cid=cid,
                ctry=cell(r["country"]),
                parse=parse_label(r["parse"]["method"]),
                l1v=fmt(l1["passed"]) if l1 else "-",
                ew="{}/{}".format(l1["n_errors"], l1["n_warnings"]) if l1 else "-",
                st=l1["state_count"] if l1 else "-",
                cov=fmt(l2["coverage"]) if l2 else "-",
                prec=fmt(l2["precision"]) if l2 else "-",
                comb=fmt(l2["combined"]) if l2 else "-",
                chk=fmt(l3["checklist_passed"]) if l3 else "-",
                bias=len(l3["bias_flags"]) if l3 else "-",
                stake=fmt(l3["stakeholder_coverage"], ".2f") if l3 else "-",
                scov=fmt(sem.get("coverage")),
                savd=fmt(sem.get("avoidance")),
                sem=fmt(sem.get("score")),
                f1=fmt(r["self_consistency_f1"]),
                overall=fmt(r["overall_passed"]),
            )
        )
    return "\n".join(out)


def render_run_summaries(agg) -> str:
    out = [
        "| Run | Strict parse | L1 pass | L3 checklist | Bias-free | Overall pass "
        "| L2 cov | L2 prec | L2 comb | Sem cov | Sem avd | Sem | States | SelfF1 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for model in MODELS:
        for condition in CONDITIONS:
            a = agg["runs"][f"{model}__{condition}"]
            out.append(
                "| {run} | {sp}/14 | {l1}/14 | {l3}/14 | {bf}/14 | {ov}/14 "
                "| {cov} | {prec} | {comb} | {scov} | {savd} | {sem} | {st} | {f1} |".format(
                    run=f"{model} ({condition})",
                    sp=a["strict_parse"], l1=a["lane1_pass"], l3=a["lane3_checklist_pass"],
                    bf=a["bias_free"], ov=a["overall_pass"],
                    cov=fmt(a["mean_lane2_coverage"]), prec=fmt(a["mean_lane2_precision"]),
                    comb=fmt(a["mean_lane2_combined"]), scov=fmt(a["mean_sem_coverage"]),
                    savd=fmt(a["mean_sem_avoidance"]), sem=fmt(a["mean_sem_score"]),
                    st=fmt(a["mean_states"], ".1f"), f1=fmt(a["mean_self_consistency"]),
                )
            )
    return "\n".join(out)

def render_case_table(agg) -> str:
    """Pooled-over-runs difficulty table: one row per case."""
    out = [
        "| Case | Country | Ref states | Ref terminals | Expected | Forbidden "
        "| L1 pass | Overall pass | Mean L2 comb | Mean Sem |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cid in CASE_IDS:
        a = agg["cases"][cid]
        out.append(
            "| {cid} | {ctry} | {rs} | {rt} | {ne} | {nf} | {l1}/6 | {ov}/6 | {comb} | {sem} |".format(
                cid=cid, ctry=cell(a["country"]), rs=a["ref_states"], rt=a["ref_terminals"],
                ne=a["n_expected"] if a["n_expected"] is not None else "-",
                nf=a["n_forbidden"] if a["n_forbidden"] is not None else "-",
                l1=a["lane1_pass"], ov=a["overall_pass"],
                comb=fmt(a["mean_lane2_combined"]), sem=fmt(a["mean_sem_score"]),
            )
        )
    return "\n".join(out)


def render_location_effect(records, agg) -> str:
    """Per-model deltas and the 14-row per-case delta/self-consistency table."""
    models_line = [
        "| Model | Mean Sem (anon) | Mean Sem (w/ loc) | Δ Sem | Mean L2 comb (anon) "
        "| Mean L2 comb (w/ loc) | Δ comb | Self-consistency F1 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for model in MODELS:
        a = agg["models"][model]
        anon = agg["runs"][f"{model}__anonymized"]
        wloc = agg["runs"][f"{model}__with_location"]
        models_line.append(
            "| {m} | {a1} | {a2} | {d1} | {b1} | {b2} | {d2} | {f1} |".format(
                m=model, a1=fmt(anon["mean_sem_score"]), a2=fmt(wloc["mean_sem_score"]),
                d1="{:+.3f}".format(a["delta_sem"]) if a["delta_sem"] is not None else "-",
                b1=fmt(anon["mean_lane2_combined"]), b2=fmt(wloc["mean_lane2_combined"]),
                d2="{:+.3f}".format(a["delta_combined"]) if a["delta_combined"] is not None else "-",
                f1=fmt(a["mean_self_consistency"]),
            )
        )

    per_case = [
        "| Case | " + " | ".join(f"{m} Δ Sem | {m} Δ comb | {m} SelfF1" for m in MODELS) + " |",
        "|---|" + "---|" * (3 * len(MODELS)),
    ]
    for cid in CASE_IDS:
        cells = [cid]
        for model in MODELS:
            sel = {r["condition"]: r for r in records
                   if r["model"] == model and r["case"] == cid}
            anon, wloc = sel.get("anonymized"), sel.get("with_location")
            if not (anon and wloc and anon["semantic"] and wloc["semantic"]):
                cells += ["-", "-", fmt(anon["self_consistency_f1"]) if anon else "-"]
                continue
            d_sem = wloc["semantic"]["score"] - anon["semantic"]["score"]
            d_comb = (wloc["lane2"]["combined"] - anon["lane2"]["combined"]
                      if anon["lane2"] and wloc["lane2"] else None)
            cells += ["{:+.3f}".format(d_sem),
                      "{:+.3f}".format(d_comb) if d_comb is not None else "-",
                      fmt(anon["self_consistency_f1"])]
        per_case.append("| " + " | ".join(cells) + " |")
    return "\n".join(models_line) + "\n\n" + "\n".join(per_case)


def render_rules(agg) -> str:
    out = ["| Rule | Occurrences | Example message (first seen) |", "|---|---|---|"]
    for entry in agg["rules"]:
        out.append("| {rule} | {count} | {example} |".format(
            rule=cell(entry["rule"]), count=entry["count"],
            example=cell(entry["example"])[:160]))
    if not agg["rules"]:
        out.append("| (none) | 0 | every candidate passed every mechanical rule |")
    return "\n".join(out)

def render_flags(agg) -> str:
    """Per-run semantic flags and bias flags, as bullet lists."""
    out = []
    for model in MODELS:
        for condition in CONDITIONS:
            a = agg["runs"][f"{model}__{condition}"]
            out.append(f"**{model} ({condition})**")
            if a["semantic_flags"]:
                out.append("- Semantic flags: " + "; ".join(
                    f"{cell(label)} (x{count})" for label, count in a["semantic_flags"]))
            else:
                out.append("- Semantic flags: none")
            if a["bias_flags"]:
                out.append("- Bias-scan flags: " + "; ".join(
                    f"{cell(label)} (x{count})" for label, count in a["bias_flags"]))
            else:
                out.append("- Bias-scan flags: none")
            if a["top_missing"]:
                out.append("- Most-missed expected ingredients: " + "; ".join(
                    f"\"{cell(bullet)}\" (missed by {count}/14)" for bullet, count in a["top_missing"]))
            out.append("")
    return "\n".join(out)


def render_findings(records, agg) -> str:
    """Auto-derived headline observations from the aggregates."""
    bullets = []
    runs = agg["runs"]
    best_sem = max(runs, key=lambda k: runs[k]["mean_sem_score"] or -1)
    best_comb = max(runs, key=lambda k: runs[k]["mean_lane2_combined"] or -1)
    bullets.append(
        f"- Best semantic expect/avoid score: **{best_sem}** "
        f"(mean Sem {runs[best_sem]['mean_sem_score']:.3f}); "
        f"best structural match: **{best_comb}** "
        f"(mean L2 combined {runs[best_comb]['mean_lane2_combined']:.3f})."
    )
    hardest = min(agg["cases"], key=lambda c: agg["cases"][c]["mean_sem_score"] or 1.0)
    easiest = max(agg["cases"], key=lambda c: agg["cases"][c]["mean_sem_score"] or -1.0)
    bullets.append(
        f"- Hardest case (pooled over 6 runs): **{hardest} ({agg['cases'][hardest]['country']})** "
        f"with mean Sem {agg['cases'][hardest]['mean_sem_score']:.3f}; easiest: **{easiest} "
        f"({agg['cases'][easiest]['country']})** at {agg['cases'][easiest]['mean_sem_score']:.3f}."
    )
    failures = [(r["model"], r["condition"], r["case"],
                 sorted({e["rule"] for e in r["lane1"]["errors"]}))
                for r in records if r["lane1"] and not r["lane1"]["passed"]]
    if failures:
        bullets.append(f"- Lane 1 mechanical failures: {len(failures)} of 84 candidates —")
        for model, condition, cid, rules in failures:
            bullets.append(f"  - {model} ({condition}) {cid}: {', '.join(rules)}")
    else:
        bullets.append("- Lane 1: all 84 mechanically valid candidates (0 errors).")
    fencing = {m: runs[f"{m}__anonymized"]["recovered"] + runs[f"{m}__with_location"]["recovered"]
               for m in MODELS}
    if any(fencing.values()):
        bullets.append(
            "- Strict tier-0 packaging failures (fenced/annotated replies that needed lenient "
            "recovery): " + ", ".join(f"{m} x{n}" for m, n in fencing.items() if n) +
            " — a generation-reliability issue, not a model-quality one."
        )
    broken = [(r["model"], r["condition"], r["case"], r["parse"].get("error", ""))
              for r in records if r["parse"]["method"] == "failed"]
    if broken:
        bullets.append(f"- Unparsable blocks (no JSON recovered): {len(broken)} of 84 —")
        for model, condition, cid, err in broken:
            bullets.append(f"  - {model} ({condition}) {cid}: {cell(err)}")
    for model in MODELS:
        a = agg["models"][model]
        if a["mean_self_consistency"] is not None:
            bullets.append(
                f"- {model}: revealing the country changes the semantic score by "
                f"{a['delta_sem']:+.3f} and structure by {a['delta_combined']:+.3f} on average; "
                f"its two versions of the same case agree at self-F1 {a['mean_self_consistency']:.3f}."
            )
    return "\n".join(bullets)

def render_readme_top(records, agg, mismatches, inventory) -> str:
    add = []
    w = add.append
    w("# Cultural Track — Raw LLM Transcripts and Three-Lane Evaluation")
    w("")
    w("This folder holds the raw LLM transcripts for the 14 cultural-norm cases (C1-C14,")
    w("`data/Test_Cases/04_cultural`) under two prompt conditions, plus the full evaluation")
    w("of every candidate through the repository's modular pipeline `src/evaluation` and the")
    w("case bank's semantic expect/avoid scorer. Everything below is computed by")
    w("`analyze_cultural_outputs.py` — rerun it to regenerate this README and the JSON in")
    w("`analysis/`.")
    w("")
    w("- **Models:** " + ", ".join(MODELS) + ".")
    w("- **Conditions:** `anonymized` = the country label in the LLM input is replaced by")
    w("  \"Location\" (bank `cultural_without_loc`); `with_location` = the country is named")
    w("  (bank `04_cultural`). The two banks state the same judging criteria; in "
      + f"{len(mismatches)} bullet(s) across "
      + ", ".join(sorted({m.split('.')[0] for m in mismatches}) or [])
      + " the anonymized bank swaps the country-specific word for a country-neutral one")
    w("  (e.g. \"laïcité\" -> \"secularism\", \"Japanese norm\" -> \"local norm\"), so each")
    w("  condition is scored against its own bank's wording.")
    w("- **Volume:** 6 transcripts x 14 cases = **84 candidates**, one sample each.")
    w("")
    w("## 1. Contents")
    w("")
    w("| File | Model | Condition | Provider (per header line) | Bytes |")
    w("|---|---|---|---|---|")
    for row in inventory:
        w("| `{}` | {} | {} | {} | {} |".format(*row))
    w("")
    w("Produced by the analysis: `analysis/cultural_pipeline_results.json` (full records),")
    w("`analysis/aggregates.json` (per-run/per-case aggregates), and the pipeline's own")
    w("artifact `analysis/evaluation_results/<model>__<condition>/<case>/evaluation_report.json`")
    w("for each of the 84 candidates.")
    w("")
    w("## 2. Structure of the transcripts")
    w("")
    w("Every transcript follows one layout:")
    w("")
    w("```text")
    w("provider: <provider> | cases: 14 | system: zero_shot_v2_prompt.md")
    w("")
    w("===== C1 (<country-or-'Location'>) — # Test Case C.1 (<Country>): <title> =====")
    w("<one JSON world model in the v2 schema — players / initial / states with turn, by, next>")
    w("")
    w("===== C2 (...) — ... =====")
    w("...")
    w("```")
    w("")
    w("Packaging quirks that matter for strict tier-0 parsing (the repository's no-strip")
    w("policy): the table below counts how each run's 14 replies parsed.")
    w("")
    w("| Run | strict ok | recovered (fence/brace) | unparsable |")
    w("|---|---|---|---|")
    for model in MODELS:
        for condition in CONDITIONS:
            a = agg["runs"][f"{model}__{condition}"]
            w("| {} ({}) | {} | {} | {} |".format(
                model, condition, a["strict_parse"], a["recovered"], a["parse_failed"]))
    w("")
    w("## 3. Methodology")
    w("")
    w("| Lane | Source | What it measures |")
    w("|---|---|---|")
    w("| Lane 0 (parse report) | this script | strict JSON parse of the block as-is; a lenient "
      "recovery (fence/brace) is recorded separately so quality is still scored when only the "
      "packaging is wrong |")
    w("| Lane 1 mechanical | `src/evaluation/lane1_mechanical.py` | schema keys, unique ids, "
      "positive probabilities summing to 1 (tol 1e-3), transitions to declared states, complete "
      "joint-action profiles, reachability, path-to-terminal (G-rules) |")
    w("| Lane 2 structural | `src/evaluation/lane2_structural.py` | coverage / precision / "
      "combined F1 of the candidate against the case's authored reference model "
      "(`data/Test_Cases/04_cultural/reference_models.json`, converted v1 to v2 by "
      "`evaluate_cultural.to_v2`) |")
    w("| Lane 3 qualitative | `src/evaluation/lane3_qualitative.py` | checklist (stakeholders "
      "present and described, non-terminal actions, states described, consequences) plus the "
      "bias scan (sensitive/proxy terms, action-profile disparity); flags are diagnostic, not "
      "verdicts |")
    w("| Semantic lane | `evaluate_cultural.eval_lane3` | expect/avoid ingredient scoring "
      "against the case's parsed judging criteria: coverage of expected bullets (partial = 0.5) "
      "with lexical/stem/synonym evidence, flags on forbidden content, score = "
      "sqrt(coverage x avoidance) |")
    w("| Self-consistency | `evaluate_structural` | feature-multiset F1 between a model's own "
      "two versions of the same case (anonymized vs. with_location) |")
    w("")
    w("**Backend disclosure.** The external `game_matching` package is not available in this")
    w("workspace, so Lane 2 runs on the pipeline's documented `feature_multiset_fallback`")
    w("backend: name-insensitive feature overlap (players, terminal/non-terminal counts, turn")
    w("arities, profile counts, transition supports). These scores are comparable across")
    w("candidates and runs but are **not** optimal graph-matching scores and must not be")
    w("presented as such (the same disclosure is made in `experiments/openrouter_game_study/`).")
    w("")
    w("`overall_passed` is the pipeline's own gate: Lane 1 passes AND Lane 3 checklist passes")
    w("AND (a reference is always given here) Lane 2 combined score > 0.")
    w("")
    w("## 4. Reproduce")
    w("")
    w("```powershell")
    w("python test_eval_pipeline.py                          # smoke-test the 3-lane pipeline")
    w("python report/raw_output/analyze_cultural_outputs.py  # rebuild everything below")
    w("```")
    w("")
    w("## 5. Headline results (per run)")
    w("")
    w(render_run_summaries(agg))
    w("")
    return "\n".join(add)

def render_readme_bottom(records, agg) -> str:
    add = []
    w = add.append
    w("## 6. Detailed per-run tables (all 14 cases x all metrics)")
    w("")
    w("Column key: **Parse** = how the raw block parsed (`ok` strict / `fence` / `brace`);")
    w("**L1** = mechanical verdict, **E/W** = errors/warnings; **States** = declared states;")
    w("**L2 cov/prec/comb** = Lane 2 coverage, precision, combined F1 vs. the authored")
    w("reference; **L3 chk** = qualitative checklist, **Bias** = number of bias-scan flags,")
    w("**StakeCov** = fraction of the reference's players present in the candidate;")
    w("**Sem cov/avd/Sem** = semantic coverage, avoidance, and their geometric mean;")
    w("**SelfF1** = agreement between this model's two condition-versions of the case;")
    w("**Overall** = the pipeline's overall gate. A `-` means the lane did not run (e.g. the")
    w("block could not be parsed).")
    w("")
    n = 1
    for model in MODELS:
        for condition in CONDITIONS:
            w(f"### 6.{n} {model} — {condition}")
            w("")
            w(render_run_table(records, model, condition))
            w("")
            n += 1
    w("## 7. Case difficulty (pooled over the 6 runs)")
    w("")
    w(render_case_table(agg))
    w("")
    w("## 8. Effect of revealing the country")
    w("")
    w(render_location_effect(records, agg))
    w("")
    w("`d Sem` / `d comb` = with_location minus anonymized (positive = knowing the country")
    w("helped). `SelfF1` = structural agreement between the two versions.")
    w("")
    w("## 9. Lane 1 failure taxonomy (all 84 candidates)")
    w("")
    w(render_rules(agg))
    w("")
    w("## 10. Semantic flags, bias flags, missed ingredients")
    w("")
    w(render_flags(agg))
    w("## 11. Findings")
    w("")
    w(render_findings(records, agg))
    w("")
    w("## 12. Limitations")
    w("")
    w("- Lane 2 uses the feature-multiset fallback (no `game_matching`); scores are")
    w("  structure-only and name-insensitive, and the authored references are one target per")
    w("  open-ended case, so low coverage can also mean *a different but acceptable* modelling")
    w("  choice rather than an omission.")
    w("- The semantic lane is lexical (stems + synonym families); it proves presence of an")
    w("  ingredient, not its correctness — a candidate can repeat the case's nouns without")
    w("  modelling the norm. Read `missing_bullets` / `partial_bullets` / `flags` in")
    w("  `analysis/cultural_pipeline_results.json` for the per-bullet evidence.")
    w("- One sample per (model, condition, case): the numbers describe these 84 artifacts, not")
    w("  the models' expected behaviour under resampling.")
    w("- Bias-scan flags (sensitive terms, action-count disparity) are diagnostic only and")
    w("  require human or counterfactual review before being called bias.")
    w("")
    return "\n".join(add) + "\n"


# --------------------------------------------------------------------------- #
# Entry point                                                                   #
# --------------------------------------------------------------------------- #

def main() -> int:
    records, raw_refs, mismatches = run_batch()
    _, refs_v2 = load_references()
    agg = aggregate(records, refs_v2)

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = ANALYSIS_DIR / "cultural_pipeline_results.json"
    results_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    (ANALYSIS_DIR / "aggregates.json").write_text(
        json.dumps(agg, indent=2, ensure_ascii=False), encoding="utf-8")

    inventory = []
    for (model, condition), fname in TRANSCRIPTS.items():
        path = RAW_DIR / fname
        header, _ = parse_transcript(path)
        inventory.append((fname, model, condition, header.get("provider", "?"),
                          path.stat().st_size))

    readme = render_readme_top(records, agg, mismatches, inventory) + \
        render_readme_bottom(records, agg)
    (RAW_DIR / "README.md").write_text(readme, encoding="utf-8")

    print(f"evaluated {len(records)} candidates across {len(TRANSCRIPTS)} transcripts")
    for model in MODELS:
        for condition in CONDITIONS:
            a = agg["runs"][f"{model}__{condition}"]
            print("  {:22} L1 {}/14  overall {}/14  L2 {:.3f}  Sem {:.3f}".format(
                f"{model}/{condition}", a["lane1_pass"], a["overall_pass"],
                a["mean_lane2_combined"] or 0.0, a["mean_sem_score"] or 0.0))
    print(f"wrote {results_path}")
    print(f"wrote {RAW_DIR / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())