"""Compare the common five-model outputs within every S, C, and G scenario.

Only like-for-like actual outputs are compared: generation 0 / repair 0 for the
situational track, the location-revealed condition for the cultural track, and each
of the three independent game runs.  Derived cultural rows and repair attempts are
excluded from agreement estimates but remain documented in the inventory.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.evaluate_python_situational import probe
from src.evaluation.lane1_mechanical import evaluate_mechanical
from src.evaluation.lane3_qualitative import evaluate_qualitative
import evaluate_cultural as cultural

OUT = ROOT / "results" / "cross_model_comparison"
MODELS = ("claude", "deepseek", "gpt", "llama", "qwen")

MODEL_ALIASES = {
    "claude-opus-5": "claude", "claude_opus_5": "claude", "opus5": "claude",
    "deepseek-v4-flash": "deepseek", "deepseek_v4_flash": "deepseek", "deepseek": "deepseek",
    "gpt-5.6-sol": "gpt", "gpt_5_6_sol": "gpt", "gpt5-6sol": "gpt",
    "llama-3.3-70b": "llama", "llama_3_3_70b": "llama", "llama3-3": "llama",
    "qwen3.8-27b": "qwen", "qwen_3_8_27b": "qwen", "qwen3-8": "qwen",
}


def features(model: Mapping[str, Any]) -> Counter[str]:
    """The evaluator's documented name-insensitive fallback feature multiset."""
    out: Counter[str] = Counter()
    out["players"] = len(model.get("players", []) or [])
    out["initial_support"] = len(model.get("initial", []) or [])
    for state in model.get("states", []) or []:
        terminal = bool(state.get("terminal", False))
        out["terminal_states" if terminal else "nonterminal_states"] += 1
        out[f"turn_arity:{len(state.get('turn', []) or [])}"] += 1
        actions = state.get("actions", []) or []
        out[f"profiles_per_state:{len(actions)}"] += 1
        for action in actions:
            successors = action.get("next", []) or []
            out[f"transition_support:{len(successors)}"] += 1
            out["transition_edges"] += len(successors)
    return out


def f1(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    a, b = features(left), features(right)
    overlap = sum(min(n, b[k]) for k, n in a.items())
    coverage = overlap / sum(a.values()) if a else 0.0
    precision = overlap / sum(b.values()) if b else 0.0
    return 2 * coverage * precision / (coverage + precision) if coverage + precision else 0.0


def situation_rows() -> list[dict[str, Any]]:
    refs = json.loads((ROOT / "data/reference_models/situational_provisional_v2.json").read_text())
    rows = []
    pattern = re.compile(r"^(S\d+)_(.+)_v2_python_g0_r0\.py$")
    for path in sorted((ROOT / "results/python-situational/generated_python").glob("*g0_r0.py")):
        match = pattern.match(path.name)
        if not match:
            continue
        case, raw_model = match.groups()
        checked = probe(path, 20)
        model = checked.get("v2") if checked.get("status") == "PASS" else None
        exploration = checked.get("exploration") or {}
        expected_players = len(refs[case]["players"])
        rows.append({
            "domain": "situational", "replicate": "g0", "case": case,
            "model": MODEL_ALIASES[raw_model], "valid": model is not None,
            "candidate": model, "bias_flags": (evaluate_qualitative(model)["details"]["bias_flags"] if model else []),
            "ethical_coverage": min((exploration.get("n_players") or 0) / expected_players, 1.0),
            "human_agency": exploration.get("human_action_width_max"),
        })
    return rows


def cultural_rows() -> list[dict[str, Any]]:
    # Reparse the real with-location transcripts; do not use the derived DeepSeek condition.
    import report.report.raw_output.analyze_cultural_outputs as analysis
    bank = {case.cid: case for case in cultural.load_cases(cases_dir=cultural.CASES_DIR)}
    rows = []
    for (raw_model, condition), filename in analysis.TRANSCRIPTS.items():
        if condition != "with_location":
            continue
        _, blocks = analysis.parse_transcript(analysis.RAW_DIR / filename)
        for block in blocks:
            raw, method = analysis.extract_json(block["raw"])
            candidate = None
            if raw is not None:
                try:
                    candidate, _ = cultural.to_v2(json.loads(json.dumps(raw)))
                except cultural.ConvertError:
                    pass
            semantic = cultural.eval_lane3(bank[block["case"]], candidate, cultural.flatten_text(raw)) if candidate else None
            qualitative = evaluate_qualitative(candidate) if candidate else None
            mechanically_valid = candidate is not None and evaluate_mechanical(candidate)["passed"]
            rows.append({
                "domain": "cultural", "replicate": "with_location", "case": block["case"],
                "model": MODEL_ALIASES[raw_model], "valid": mechanically_valid,
                "candidate": candidate if mechanically_valid else None,
                "bias_flags": qualitative["details"]["bias_flags"] if qualitative else [],
                "ethical_coverage": semantic["coverage"] if semantic else None,
                "forbidden_flags": semantic["n_flagged_bullets"] if semantic else None,
            })
    return rows


def game_rows() -> list[dict[str, Any]]:
    summary = list(csv.DictReader((ROOT / "experiments/openrouter_game_study/evaluation_summary.csv").open()))
    rows = []
    for item in summary:
        path = ROOT / "experiments/openrouter_game_study" / item["run"] / "04_world_models" / item["tag"] / "world_model.json"
        valid = item["lane1_passed"] == "True"
        candidate = canonical_to_v2(json.loads(path.read_text())) if path.exists() and valid else None
        rows.append({
            "domain": "game", "replicate": item["run"], "case": item["case"],
            "model": MODEL_ALIASES[item["model"]], "valid": valid,
            "candidate": candidate, "bias_flags": [], "ethical_coverage": None,
        })
    return rows


def canonical_to_v2(document: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a saved canonical Python rollout without importing EDA dependencies."""
    players = [str(player) for player in document["players"]]
    transitions: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for transition in document["transitions"]:
        transitions[str(transition["state"])].append(transition)
    states = []
    for state in document["states"]:
        state_id, terminal = str(state["id"]), bool(state["terminal"])
        if terminal:
            states.append({"id": state_id, "terminal": True, "turn": [], "actions": []})
            continue
        turn = [player for player in players if player in (state.get("actions") or {})]
        actions = []
        for transition in transitions[state_id]:
            actions.append({
                "by": {player: str(transition["joint_action"][player]) for player in turn},
                "next": [{"state": str(outcome["next_state"]), "p": float(outcome["probability"])}
                         for outcome in transition["outcomes"] if float(outcome["probability"]) > 0],
            })
        states.append({"id": state_id, "terminal": False, "turn": turn, "actions": actions})
    return {
        "players": [{"id": player, "desc": f"game participant {player}"} for player in players],
        "initial": [{"state": str(item["state"]), "p": float(item["probability"])}
                    for item in document["initial_distribution"]],
        "states": states,
    }


def comparisons(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["domain"], row["replicate"], row["case"])].append(row)
    scenario, pairs = [], []
    for (domain, replicate, case), items in sorted(grouped.items()):
        by_model = {row["model"]: row for row in items}
        validity = [by_model[m]["valid"] for m in MODELS]
        scores = []
        for left, right in combinations(MODELS, 2):
            a, b = by_model[left].get("candidate"), by_model[right].get("candidate")
            score = f1(a, b) if a is not None and b is not None else None
            pairs.append({"domain": domain, "replicate": replicate, "case": case,
                          "model_a": left, "model_b": right, "structural_f1": score})
            if score is not None:
                scores.append(score)
        coverages = [row["ethical_coverage"] for row in items if row.get("ethical_coverage") is not None]
        scenario.append({
            "domain": domain, "replicate": replicate, "case": case,
            "models_present": len(by_model), "valid_models": sum(validity),
            "unanimous_validity": len(set(validity)) == 1,
            "pairwise_comparisons": len(scores),
            "mean_pairwise_structural_f1": mean(scores) if scores else None,
            "min_pairwise_structural_f1": min(scores) if scores else None,
            "max_pairwise_structural_f1": max(scores) if scores else None,
            "mean_criteria_coverage_proxy": mean(coverages) if coverages else None,
            "bias_flagged_models": sum(bool(row.get("bias_flags")) for row in items),
            "forbidden_flag_total": sum(row.get("forbidden_flags") or 0 for row in items),
        })
    return scenario, pairs


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: json.dumps(value) if isinstance(value, list) else value
                          for key, value in row.items()} for row in rows)


def main() -> None:
    rows = situation_rows() + cultural_rows() + game_rows()
    scenarios, pairs = comparisons(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    public_rows = [{k: v for k, v in row.items() if k != "candidate"} for row in rows]
    write_csv(OUT / "model_scenario_metrics.csv", public_rows)
    write_csv(OUT / "scenario_agreement.csv", scenarios)
    write_csv(OUT / "pairwise_structural_similarity.csv", pairs)
    model_summary = []
    for domain in ("situational", "cultural", "game"):
        for model in MODELS:
            items = [row for row in rows if row["domain"] == domain and row["model"] == model]
            coverage = [row["ethical_coverage"] for row in items if row.get("ethical_coverage") is not None]
            model_summary.append({
                "domain": domain, "model": model, "outputs": len(items),
                "valid_outputs": sum(row["valid"] for row in items),
                "validity_rate": sum(row["valid"] for row in items) / len(items),
                "mean_criteria_coverage_proxy": mean(coverage) if coverage else None,
                "bias_flagged_outputs": sum(bool(row.get("bias_flags")) for row in items),
                "forbidden_flag_total": sum(row.get("forbidden_flags") or 0 for row in items),
                "human_choice_outputs": sum((row.get("human_agency") or 0) > 1 for row in items),
            })
    write_csv(OUT / "summary_by_model.csv", model_summary)
    pair_summary = []
    for domain in ("situational", "cultural", "game"):
        for left, right in combinations(MODELS, 2):
            scores = [row["structural_f1"] for row in pairs if row["domain"] == domain
                      and row["model_a"] == left and row["model_b"] == right
                      and row["structural_f1"] is not None]
            pair_summary.append({"domain": domain, "model_a": left, "model_b": right,
                                 "comparable_scenarios": len(scores),
                                 "mean_structural_f1": mean(scores) if scores else None})
    write_csv(OUT / "summary_by_model_pair.csv", pair_summary)
    inventory = {
        "situational": {"actual_common_condition": "g0_r0", "rows": 55, "cases": 11, "models": 5,
                        "stored_files_all_repairs": 217},
        "cultural": {"actual_common_condition": "with_location", "rows": 70, "cases": 14, "models": 5,
                     "anonymized_actual_models": 4, "deepseek_anonymized": "derived, excluded"},
        "game": {"actual_common_condition": "three runs", "rows": 135, "cases": 9, "models": 5, "runs": 3},
    }
    compared_inputs = sorted(
        list((ROOT / "results/python-situational/generated_python").glob("*g0_r0.py"))
        + list((ROOT / "report/report/raw_output").glob("cultural_*w_loc.txt"))
        + list((ROOT / "report/report/raw_output").glob("cultural_qwen3.8_w_loc.log"))
        + list((ROOT / "experiments/openrouter_game_study").glob("run_[123]/04_world_models/*/world_model.json"))
    )
    inventory["provenance"] = {
        "execution": "offline CPU analysis of repository artifacts; no LLM calls",
        "command": "python experiments/compare_five_model_outputs.py",
        "input_file_count": len(compared_inputs),
        "input_sha256": hashlib.sha256(
            b"".join(str(path.relative_to(ROOT)).encode() + b"\0" + path.read_bytes()
                     for path in compared_inputs)
        ).hexdigest(),
    }
    aggregates = {}
    for domain in ("situational", "cultural", "game"):
        sr = [row for row in scenarios if row["domain"] == domain]
        scores = [row["mean_pairwise_structural_f1"] for row in sr if row["mean_pairwise_structural_f1"] is not None]
        aggregates[domain] = {
            "scenario_replicates": len(sr),
            "all_have_five_models": all(row["models_present"] == 5 for row in sr),
            "unanimous_validity_rate": sum(row["unanimous_validity"] for row in sr) / len(sr),
            "mean_pairwise_structural_f1": mean(scores),
            "lowest_agreement": min(sr, key=lambda row: row["mean_pairwise_structural_f1"] if row["mean_pairwise_structural_f1"] is not None else 2),
            "highest_agreement": max(sr, key=lambda row: row["mean_pairwise_structural_f1"] or -1),
            "bias_flagged_model_outputs": sum(row["bias_flagged_models"] for row in sr),
            "forbidden_flag_total": sum(row["forbidden_flag_total"] for row in sr),
        }
    (OUT / "summary.json").write_text(json.dumps({"inventory": inventory, "aggregates": aggregates}, indent=2) + "\n")
    print(json.dumps({"inventory": inventory, "aggregates": aggregates}, indent=2))

if __name__ == "__main__":
    main()
