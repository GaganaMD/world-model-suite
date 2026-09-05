"""Regenerate paper analyses from the 135 preserved game-study artifacts.

No model APIs are called. Lane 2 uses the repository-pinned game_matching
revision after the existing finite-horizon POSG conversion. Historical
feature-multiset scores remain in every per-trial row for comparison.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
import networkx as nx
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from json_generation.lane2 import lane2_score
from src.evaluation.pipeline import _load_model

STUDY = ROOT / "experiments" / "openrouter_game_study"
RESULTS = STUDY / "paper_results"
FIGURES = RESULTS / "figures"
PAPER_FIGURES = ROOT / "overleaf" / "World Models Workshop" / "fig"
REFERENCES = ROOT / "json_generation" / "reference_models.json"
RUNS = ("run_1", "run_2", "run_3")
SA_ITERS = 3_000
SEED = 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def quantile(values: Iterable[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def distribution(values: list[float]) -> dict[str, float | int]:
    q1, q3 = quantile(values, .25), quantile(values, .75)
    return {
        "n": len(values), "mean": statistics.mean(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values), "q1": q1, "median": statistics.median(values),
        "q3": q3, "iqr": q3 - q1, "max": max(values),
        "exact": sum(math.isclose(x, 1.0, abs_tol=1e-9) for x in values),
        "at_least_090": sum(x >= .90 for x in values),
        "at_least_075": sum(x >= .75 for x in values),
        "below_075": sum(x < .75 for x in values),
    }


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return center - half, center + half


def graph_metrics(model: dict[str, Any]) -> dict[str, float | int | bool]:
    states = model.get("states", []) or []
    graph = nx.DiGraph()
    graph.add_nodes_from(str(s["id"]) for s in states)
    profiles = edges = stochastic = 0
    entropies: list[float] = []
    branching: list[int] = []
    for state in states:
        successors_for_state: set[str] = set()
        for action in state.get("actions", []) or []:
            profiles += 1
            outcomes = [o for o in action.get("next", []) or [] if float(o.get("p", 0)) > 0]
            if len(outcomes) > 1:
                stochastic += 1
            entropies.append(-sum(float(o["p"]) * math.log2(float(o["p"])) for o in outcomes))
            for outcome in outcomes:
                source, target = str(state["id"]), str(outcome["state"])
                graph.add_edge(source, target)
                successors_for_state.add(target)
                edges += 1
        if not state.get("terminal", False):
            branching.append(len(successors_for_state))
    initial = [str(x["state"]) for x in model.get("initial", []) or []]
    reachable = set(initial)
    for start in initial:
        if start in graph:
            reachable.update(nx.descendants(graph, start))
    subgraph = graph.subgraph(reachable)
    depths: dict[str, int] = {}
    for start in initial:
        for node, depth in nx.single_source_shortest_path_length(subgraph, start).items():
            depths[node] = min(depths.get(node, depth), depth)
    return {
        "states": len(states), "terminal_states": sum(bool(s.get("terminal")) for s in states),
        "action_profiles": profiles, "transition_edges": edges,
        "avg_branching": statistics.mean(branching) if branching else 0.0,
        "max_branching": max(branching, default=0),
        "scc_count": nx.number_strongly_connected_components(subgraph),
        "cyclic": not nx.is_directed_acyclic_graph(subgraph),
        "max_depth": max(depths.values(), default=0),
        "mean_transition_entropy": statistics.mean(entropies) if entropies else 0.0,
        "stochastic_profile_fraction": stochastic / profiles if profiles else 0.0,
    }


def first_pass_map() -> dict[tuple[str, str, str], bool]:
    """Index initial unaided outcomes independently of the final repair tag."""
    result: dict[tuple[str, str, str], bool] = {}
    for run in RUNS:
        for line in (STUDY / run / "00_run_info" / "records.jsonl").read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("stage") == "first_pass":
                result[(run, record["model"], record["case"])] = record["status"] == "passed"
    return result


def structural_rows() -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    historical = read_csv(STUDY / "evaluation_summary.csv")
    refs = json.loads(REFERENCES.read_text(encoding="utf-8"))
    first_pass = first_pass_map()
    models: dict[tuple[str, str], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for index, old in enumerate(historical, 1):
        run, tag, game = old["run"], old["tag"], old["case"]
        candidate = _load_model(STUDY / run / "04_world_models" / tag / "world_model.json", "candidate")
        reference = refs[game.replace("G", "G.")]
        matched = lane2_score(reference, candidate, sa_iters=SA_ITERS, seed=SEED, use_intrinsic=True)
        candidate_metrics = graph_metrics(candidate)
        models[(run, tag)] = candidate
        row: dict[str, Any] = {
            "model": old["model"], "game": game, "run": run, "tag": tag,
            "first_pass_valid": first_pass[(run, old["model"], game)],
            "posthoc_lane1_pass": old["lane1_passed"] == "True",
            "fallback_coverage": float(old["lane2_coverage"]),
            "fallback_precision": float(old["lane2_precision"]),
            "fallback_f1": float(old["lane2_combined_score"]),
            "matched_coverage": matched["coverage"], "matched_precision": matched["precision"],
            "matched_f1": matched["lane2"], "exact_match": matched["lane2"] == 1.0,
            "mapped_players": len(matched["player_map"]),
            "mapped_reference_states": len(matched["state_map_src"]),
        }
        row.update({f"candidate_{key}": value for key, value in candidate_metrics.items()})
        rows.append(row)
        print(f"[{index:03d}/135] {run}/{tag}: fallback={row['fallback_f1']:.4f} matched={row['matched_f1']:.4f}", flush=True)
    return rows, models


def clustered_bootstrap(rows: list[dict[str, Any]], samples: int = 5_000) -> tuple[float, float]:
    by_game: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_game[row["game"]].append(row["matched_f1"])
    games = sorted(by_game)
    rng = random.Random(20260901)
    means = []
    for _ in range(samples):
        selected = [rng.choice(games) for _ in games]
        means.append(statistics.mean(score for game in selected for score in by_game[game]))
    return quantile(means, .025), quantile(means, .975)


def model_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["model"]].append(row)
    output = []
    for model, items in sorted(grouped.items()):
        first = sum(x["first_pass_valid"] for x in items)
        wilson_low, wilson_high = wilson(first, len(items))
        boot_low, boot_high = clustered_bootstrap(items)
        scores = [x["matched_f1"] for x in items]
        output.append({
            "model": model, "n": len(items), "first_pass_valid": first,
            "first_pass_rate": first / len(items), "first_pass_wilson_low": wilson_low,
            "first_pass_wilson_high": wilson_high,
            "lane1_pass": sum(x["posthoc_lane1_pass"] for x in items),
            "fallback_mean_f1": statistics.mean(x["fallback_f1"] for x in items),
            "matched_mean_coverage": statistics.mean(x["matched_coverage"] for x in items),
            "matched_mean_precision": statistics.mean(x["matched_precision"] for x in items),
            "matched_mean_f1": statistics.mean(scores), "matched_median_f1": statistics.median(scores),
            "matched_q1": quantile(scores, .25), "matched_q3": quantile(scores, .75),
            "matched_cluster_boot_low": boot_low, "matched_cluster_boot_high": boot_high,
            "exact_matches": sum(x["exact_match"] for x in items),
        })
    return output


def stability_summary(rows: list[dict[str, Any]], models: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["game"])].append(row)
    output = []
    for (model, game), items in sorted(grouped.items()):
        items.sort(key=lambda x: x["run"])
        scores = [x["matched_f1"] for x in items]
        pairwise = []
        for left, right in ((0, 1), (0, 2), (1, 2)):
            a = models[(items[left]["run"], items[left]["tag"])]
            b = models[(items[right]["run"], items[right]["tag"])]
            pairwise.append(lane2_score(a, b, sa_iters=SA_ITERS, seed=SEED, use_intrinsic=True)["lane2"])
        row: dict[str, Any] = {
            "model": model, "game": game, "n_runs": 3,
            "mean_matched_f1": statistics.mean(scores), "sd_matched_f1": statistics.stdev(scores),
            "range_matched_f1": max(scores) - min(scores),
            "cv_matched_f1": statistics.stdev(scores) / statistics.mean(scores) if statistics.mean(scores) else "",
            "all_three_exact_reference_matches": all(x["exact_match"] for x in items),
            "all_three_generations_structurally_equivalent": all(x == 1.0 for x in pairwise),
            "mean_pairwise_generation_f1": statistics.mean(pairwise),
        }
        for metric in ("states", "transition_edges", "terminal_states", "scc_count", "avg_branching", "mean_transition_entropy"):
            values = [float(x[f"candidate_{metric}"]) for x in items]
            row[f"{metric}_range"] = max(values) - min(values)
        output.append(row)
    return output


def complexity_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = json.loads(REFERENCES.read_text(encoding="utf-8"))
    metrics = {game: graph_metrics(refs[game.replace("G", "G.")]) for game in sorted({x["game"] for x in rows})}
    by_game = defaultdict(list)
    for row in rows:
        by_game[row["game"]].append(row)
    game_rows = []
    for game in sorted(by_game):
        items = by_game[game]
        record = {"game": game, **{f"reference_{k}": v for k, v in metrics[game].items()}}
        record.update({
            "mean_matched_f1": statistics.mean(x["matched_f1"] for x in items),
            "mechanical_failure_rate": 1 - sum(x["first_pass_valid"] for x in items) / len(items),
            "exact_match_rate": sum(x["exact_match"] for x in items) / len(items),
        })
        game_rows.append(record)
    selected = ("states", "terminal_states", "action_profiles", "transition_edges", "avg_branching", "stochastic_profile_fraction")
    correlations = []
    fidelity = [x["mean_matched_f1"] for x in game_rows]
    for metric in selected:
        values = [float(x[f"reference_{metric}"]) for x in game_rows]
        result = spearmanr(values, fidelity)
        correlations.append({
            "metric": metric, "n_games": len(game_rows),
            "spearman_rho_with_mean_f1": float(result.statistic),
            "two_sided_p_descriptive": float(result.pvalue),
            "direction": "positive" if result.statistic > 0 else "negative" if result.statistic < 0 else "none",
            "note": "exploratory; n=9; no causal or confirmatory inference",
        })
    write_csv(RESULTS / "per_game_complexity.csv", game_rows)
    return correlations


def failure_taxonomy(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = json.loads(REFERENCES.read_text(encoding="utf-8"))
    ref_metrics = {f"G{i}": graph_metrics(refs[f"G.{i}"]) for i in range(1, 10)}
    output = []
    for row in rows:
        if row["exact_match"]:
            continue
        ref = ref_metrics[row["game"]]
        labels = []
        if row["candidate_states"] < ref["states"]: labels.append("fewer states")
        if row["candidate_states"] > ref["states"]: labels.append("additional states / possible state splitting")
        if row["candidate_action_profiles"] < ref["action_profiles"]: labels.append("fewer action profiles")
        if row["candidate_action_profiles"] > ref["action_profiles"]: labels.append("additional action profiles")
        if row["candidate_transition_edges"] < ref["transition_edges"]: labels.append("fewer transition supports")
        if row["candidate_transition_edges"] > ref["transition_edges"]: labels.append("additional transition supports")
        if row["candidate_terminal_states"] != ref["terminal_states"]: labels.append("terminal-count mismatch")
        if row["candidate_cyclic"] != ref["cyclic"]: labels.append("cycle-presence mismatch")
        if not math.isclose(float(row["candidate_stochastic_profile_fraction"]), float(ref["stochastic_profile_fraction"]), abs_tol=1e-9):
            labels.append("stochastic-profile-rate mismatch")
        output.append({
            "model": row["model"], "game": row["game"], "run": row["run"], "tag": row["tag"],
            "lane1_pass": row["posthoc_lane1_pass"], "matched_f1": row["matched_f1"],
            "objective_difference_flags": "; ".join(labels) or "matcher disagreement without count-level flag",
            "semantic_status": "requires semantic inspection",
        })
    return output


def plots(rows: list[dict[str, Any]], stability: list[dict[str, Any]]) -> None:
    passing = [x["matched_f1"] for x in rows if x["posthoc_lane1_pass"]]
    fig, ax = plt.subplots(figsize=(5.8, 3.5))
    ordered = sorted(passing)
    ax.step(ordered, [(i + 1) / len(ordered) for i in range(len(ordered))], where="post", color="#3366AA")
    ax.axvline(.75, color="#AA3377", linestyle="--", linewidth=1, label="descriptive 0.75 cutoff")
    ax.set(xlabel="Permutation-invariant structural F1", ylabel="Empirical cumulative proportion", xlim=(0, 1.01), ylim=(0, 1.02))
    ax.grid(alpha=.25); ax.legend(frameon=False, fontsize=8); fig.tight_layout()
    for path in (FIGURES / "matched_f1_ecdf.pdf", PAPER_FIGURES / "matched_f1_ecdf.pdf"):
        fig.savefig(path)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.8, 3.5))
    by_model = defaultdict(list)
    for row in stability:
        by_model[row["model"]].append(row["range_matched_f1"])
    labels = sorted(by_model)
    ax.boxplot([by_model[x] for x in labels], tick_labels=[x.replace("_", " ") for x in labels], showfliers=True)
    ax.set_ylabel("Within-pair F1 range across three runs"); ax.tick_params(axis="x", rotation=20); ax.grid(axis="y", alpha=.25); fig.tight_layout()
    for path in (FIGURES / "within_pair_stability.pdf", PAPER_FIGURES / "within_pair_stability.pdf"):
        fig.savefig(path)
    plt.close(fig)


def failure_case_figure(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Render an evidence-backed compressed view of the audited Claude G6 graph.

    The complete generated graph has 101 nodes and is illegible at column width,
    so nodes sharing the same explicit phase prefix are grouped. Counts come from
    the preserved canonical artifact; the unsupported bid values are verified in
    the preserved raw response and case rubric.
    """
    selected = next(x for x in rows if x["run"] == "run_1" and x["tag"] == "claude_opus_5_G6_s01_r0")
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.3))
    panels = [
        (axes[0], "Reference G6", [(0, .5, "Bid decision\n1 state\n2 bids/player"), (1, .75, "P1 wins"), (1, .5, "Tie-break\n2 stochastic outcomes"), (1, .25, "P2 wins")],
         [((0,.5),(1,.75)), ((0,.5),(1,.5)), ((0,.5),(1,.25))]),
        (axes[1], "Claude Opus 5, run 1", [(0, .5, "Type draw\n1 state"), (.65, .5, "Bid phase\n4 type states\n4 bids/player"), (1.35, .65, "Tie phase\n16 states"), (1.35, .35, "Terminal\n80 states")],
         [((0,.5),(.65,.5)), ((.65,.5),(1.35,.65)), ((.65,.5),(1.35,.35)), ((1.35,.65),(1.35,.35))]),
    ]
    for ax, title, nodes, edges in panels:
        for source, target in edges:
            ax.annotate("", xy=target, xytext=source, arrowprops={"arrowstyle":"->", "color":"#555555", "lw":1.2})
        for x, y, label in nodes:
            terminal = "wins" in label.lower() or label.startswith("Terminal")
            ax.text(x, y, label, ha="center", va="center", fontsize=7.5,
                    bbox={"boxstyle":"round,pad=.35", "fc":"#DDEEFF" if not terminal else "#E5E5E5", "ec":"#335577"})
        ax.set_title(title, fontsize=9); ax.set_xlim(-.25, 1.65); ax.set_ylim(.08, .92); ax.axis("off")
    fig.suptitle("Mechanically valid but structurally expanded G6 model", fontsize=10)
    fig.tight_layout()
    for path in (FIGURES / "g6_claude_failure_case.pdf", PAPER_FIGURES / "g6_claude_failure_case.pdf",
                 PAPER_FIGURES / "g6_claude_failure_case.png"):
        fig.savefig(path, dpi=300 if path.suffix == ".png" else None)
    plt.close(fig)
    record = {
        "game": "G6", "model": "claude_opus_5", "run": "run_1", "tag": selected["tag"],
        "lane1_pass": selected["posthoc_lane1_pass"], "matched_f1": selected["matched_f1"],
        "reference_states": 5, "generated_states": selected["candidate_states"],
        "reference_action_profiles": 4, "generated_action_profiles": selected["candidate_action_profiles"],
        "verified_mismatch": "Candidate invents numeric bids 0,1,2,3 although the case specifies two bid levels and explicitly disallows invented bid amounts; it also inserts private-type and tie phases, expanding 5 reference states to 101 generated states.",
        "candidate_source": "experiments/openrouter_game_study/run_1/02_model_outputs/raw_replies/claude_opus_5_G6_s01_r0.txt",
        "case_source": "experiments/openrouter_game_study/run_1/01_inputs/game_cases/game_G_6_Game_Situation_G6.md",
    }
    (RESULTS / "failure_examples.json").write_text(json.dumps([record], indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True); FIGURES.mkdir(exist_ok=True); PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    rows, models = structural_rows()
    write_csv(RESULTS / "per_trial.csv", rows)
    write_csv(STUDY / "paper_structural_comparison.csv", rows)
    models_summary = model_summary(rows); write_csv(RESULTS / "summary.csv", models_summary)
    passing = [x for x in rows if x["posthoc_lane1_pass"]]
    stability = stability_summary(rows, models); write_csv(RESULTS / "stability.csv", stability)
    complexity = complexity_summary(rows); write_csv(RESULTS / "complexity_analysis.csv", complexity)
    failures = failure_taxonomy(rows); write_csv(RESULTS / "failure_taxonomy.csv", failures)
    plots(rows, stability)
    failure_example = failure_case_figure(rows)
    stability_by_model = []
    for model in sorted({x["model"] for x in stability}):
        items = [x for x in stability if x["model"] == model]
        stability_by_model.append({
            "model": model, "pairs": len(items),
            "mean_within_pair_sd": statistics.mean(x["sd_matched_f1"] for x in items),
            "median_within_pair_range": statistics.median(x["range_matched_f1"] for x in items),
            "all_three_exact_reference_pairs": sum(x["all_three_exact_reference_matches"] for x in items),
            "structurally_equivalent_generation_triples": sum(x["all_three_generations_structurally_equivalent"] for x in items),
        })
    write_csv(RESULTS / "stability_by_model.csv", stability_by_model)
    summary = {
        "matcher": {"backend": "game_matching", "pinned_revision": "76ca30bdfc2c44cad5fa5db98c3bdaef7d3fa629", "horizon": 3, "sa_iters": SA_ITERS, "seed": SEED, "use_intrinsic": True},
        "all_trials": distribution([x["matched_f1"] for x in rows]),
        "lane1_passing": distribution([x["matched_f1"] for x in passing]),
        "fallback_lane1_passing": distribution([x["fallback_f1"] for x in passing]),
        "models": models_summary, "stability_by_model": stability_by_model,
        "stability_overall": {
            "pairs": len(stability),
            "mean_within_pair_sd": statistics.mean(x["sd_matched_f1"] for x in stability),
            "median_within_pair_range": statistics.median(x["range_matched_f1"] for x in stability),
            "all_three_exact_reference_pairs": sum(x["all_three_exact_reference_matches"] for x in stability),
            "structurally_equivalent_generation_triples": sum(x["all_three_generations_structurally_equivalent"] for x in stability),
        },
        "complexity": complexity,
        "failure_example": failure_example,
        "failure_flag_counts": dict(Counter(flag for row in failures for flag in row["objective_difference_flags"].split("; "))),
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (STUDY / "paper_results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
