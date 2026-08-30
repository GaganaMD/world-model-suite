#!/usr/bin/env python3
"""Evaluate the zero-shot-v3 JSON-track world models with Lanes 1/2/3 + extensions.

For each candidate in ``runs/v3_json_track/*.json`` (the 10 toy cases T1.1-T4.4 and
the first two game cases G.1, G.2 — authored offline following
``prompts_library/zero_shot_v3_prompt.md``, see ``_manifest.json``), this script:

- runs the repository's three-lane pipeline on the candidate against the case's
  authored reference model (``json_generation/reference_models.json``, converted
  v1 -> v2) and saves the pipeline's own ``evaluation_report.json`` per case;
- adds **extended Lane 1 metrics** (structural statistics, distribution entropy,
  branching, terminal-depth, cyclicity/SCCs, reachability coverage);
- adds **extended Lane 2 metrics** (feature-level matched/missing/extra breakdown);
- adds **extended Lane 3 metrics** (stakeholder-id coverage, human-agency proxy,
  outcome granularity, bias-scan rules);
- builds **granular transition graphs** — one fully-annotated graph per case plus a
  per-depth (step-by-step) diagram ``depth_<d>.png`` for every BFS depth layer, so
  "as many steps as needed" are rendered for each model;

and writes everything under ``runs/v3_json_track/``:

    evaluation_results/<case>/evaluation_report.json   pipeline artifacts
    evaluation_summary.json                            per-case + aggregate metrics
    graphs/<case>/full_<case>.png                      annotated combined graph
    graphs/<case>/depth_<d>.png                        step-by-step layer diagrams
    README.md                                          this run's report

    python json_generation/evaluate_v3_json_track.py
"""
from __future__ import annotations

import datetime
import json
import math
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import evaluate_world_model  # noqa: E402
from src.evaluation.lane2_structural import _feature_counts  # noqa: E402
import evaluate_cultural as ec  # noqa: E402

RUN_DIR = ROOT / "runs" / "v3_json_track"
EVAL_DIR = RUN_DIR / "evaluation_results"
GRAPHS_DIR = RUN_DIR / "graphs"
REFERENCES = ROOT / "json_generation" / "reference_models.json"

REF_KEY = {
    "toy_1_1": "1.1", "toy_1_2": "1.2", "toy_2_1": "2.1", "toy_2_2": "2.2",
    "toy_3_1": "3.1", "toy_3_2": "3.2", "toy_4_1": "4.1", "toy_4_2": "4.2",
    "toy_4_3": "4.3", "toy_4_4": "4.4", "game_G_1": "G.1", "game_G_2": "G.2",
}


# --------------------------------------------------------------------------- #
# metric helpers                                                                #
# --------------------------------------------------------------------------- #

def shannon_entropy(probs) -> float:
    """Bits of uncertainty in a discrete distribution."""
    values = [p for p in probs if p and p > 0]
    return -sum(p * math.log2(p) for p in values)


def structural_metrics(model: dict) -> dict:
    """Extended Lane 1 numbers — structure, entropy, depth, cyclicity."""
    states = {s["id"]: s for s in model.get("states", [])}
    players = model.get("players", [])
    terminals = {sid for sid, s in states.items() if s.get("terminal", False)}
    nonterminals = [sid for sid, s in states.items() if not s.get("terminal", False)]
    entries = [e for sid in nonterminals for e in states[sid].get("actions", [])]

    branch_sizes, entropies = [], []
    for entry in entries:
        nxt = entry.get("next", [])
        branch_sizes.append(len(nxt))
        entropies.append(shannon_entropy([n["p"] for n in nxt]))

    graph = nx.DiGraph()
    for sid, s in states.items():
        graph.add_node(sid, terminal=s.get("terminal", False))
        for entry in s.get("actions", []):
            for n in entry.get("next", []):
                graph.add_edge(sid, n["state"])
    initials = [e["state"] for e in model.get("initial", [])]
    depth = {}
    for seed in initials:
        if seed not in graph:
            continue
        for node, dist in nx.single_source_shortest_path_length(graph, seed).items():
            depth[node] = min(depth.get(node, dist), dist)
    terminal_depth = [d for sid, d in depth.items() if sid in terminals]
    sccs = list(nx.strongly_connected_components(graph))
    cyclic = any(
        len(c) > 1 or any(graph.has_edge(s, s) for s in c)
        for c in sccs
    )
    return {
        "n_players": len(players),
        "n_humans": sum(1 for p in players if p.get("type") == "human"),
        "n_states": len(states),
        "n_terminal": len(terminals),
        "n_nonterminal": len(nonterminals),
        "n_joint_actions": len(entries),
        "avg_actions_per_nonterminal": round(
            len(entries) / len(nonterminals), 3) if nonterminals else 0,
        "total_transition_edges": sum(branch_sizes),
        "avg_branching": round(sum(branch_sizes) / len(branch_sizes), 3) if branch_sizes else 0,
        "avg_distribution_entropy_bits": round(sum(entropies) / len(entropies), 3)
                                        if entropies else 0,
        "max_distribution_entropy_bits": round(max(entropies), 3) if entropies else 0,
        "reachability_coverage": round(len(depth) / len(states), 3) if states else 0,
        "max_terminal_depth": max(terminal_depth) if terminal_depth else None,
        "mean_terminal_depth": round(sum(terminal_depth) / len(terminal_depth), 3)
                               if terminal_depth else None,
        "cyclic": bool(cyclic),
        "strongly_connected_components": len(sccs),
    }


def feature_diff(reference: dict, candidate: dict) -> list:
    """Per-feature Lane 2 breakdown: match / delta / missing (in ref) / extra (in cand)."""
    rf, cf = _feature_counts(reference), _feature_counts(candidate)
    rows = []
    for key in sorted(set(rf) | set(cf)):
        if key not in rf:
            status = "extra"
        elif key not in cf:
            status = "missing"
        else:
            status = "match" if rf[key] == cf[key] else "delta"
        rows.append({"feature": key, "reference": rf.get(key),
                     "candidate": cf.get(key), "status": status})
    return rows
# --------------------------------------------------------------------------- #
# granular transition graphs                                                   #
# --------------------------------------------------------------------------- #

def _edge_rows(model: dict):
    """Yield (source, target, action-label, p) for every transition in the model."""
    for s in model.get("states", []):
        sid = s["id"]
        for entry in s.get("actions", []):
            names = " + ".join(f"{p}:{a}" for p, a in sorted(entry["by"].items()))
            for n in entry.get("next", []):
                yield sid, n["state"], names, float(n["p"])


def _build_graph(model: dict, depth_limit: int | None = None):
    """nx.DiGraph carrying edge labels; optionally limited by BFS depth from initial."""
    rows = list(_edge_rows(model))
    graph = nx.DiGraph()
    for s in model.get("states", []):
        graph.add_node(s["id"], terminal=bool(s.get("terminal", False)),
                       desc=s.get("desc", ""))
    for source, target, _, _ in rows:
        graph.add_edge(source, target)
    initials = [e["state"] for e in model.get("initial", [])]
    keep = set()
    for seed in initials:
        if seed not in graph:
            continue
        for node, dist in nx.single_source_shortest_path_length(graph, seed).items():
            if depth_limit is None or dist <= depth_limit:
                keep.add(node)
    out = nx.DiGraph()
    for node, data in graph.nodes(data=True):
        if node in keep:
            out.add_node(node, **data)
    for source, target, label, p in rows:
        if source in keep and target in keep:
            edge_label = out.get_edge_data(source, target, default={}).get("label", "")
            parts = [edge_label] if edge_label else []
            parts.append(f"{label}@{p:.3g}")
            out.add_edge(source, target, label=" ; ".join(parts))
    return out


def _layered_positions(graph: nx.DiGraph, initials: list, terminals: set) -> dict:
    """Depth-based layout: layer 0 at the top, terminals on a shared bottom layer."""
    depth = {}
    for seed in initials:
        if seed not in graph:
            continue
        for node, dist in nx.single_source_shortest_path_length(graph, seed).items():
            depth[node] = min(depth.get(node, dist), dist)
    bottom = max(depth.values(), default=0)
    positions = {}
    for index, node in enumerate(graph):
        layer = bottom - depth.get(node, 0)
        if node in terminals:
            layer = 0
        positions[node] = (index, layer)
    return positions


def _draw(graph, save_path, title, subtitle="", node_size=3000):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.close("all")
    figure, axis = plt.subplots(figsize=(13, 7), constrained_layout=True)
    axis.set_facecolor("#f8fafc")
    figure.set_facecolor("#f8fafc")
    initials = [n for n in graph if graph.nodes[n].get("init", False)]
    terminals = {n for n in graph if graph.nodes[n].get("terminal", False)}
    graph_nodes = list(graph.nodes)
    if not initials:
        initials = graph_nodes[:1]
    positions = _layered_positions(graph, initials, terminals)
    colors = ["#2563eb" if n in initials else
              "#f97316" if n in terminals else "#64748b" for n in graph_nodes]
    nx.draw_networkx_nodes(graph, positions, node_color=colors,
                           node_size=node_size, ax=axis)
    labels = {n: f"{n}\n{graph.nodes[n].get('desc', '')[:60]}" for n in graph_nodes}
    nx.draw_networkx_labels(graph, positions, labels=labels,
                            font_color="white", font_weight="bold",
                            font_size=6.5, ax=axis)
    nx.draw_networkx_edges(graph, positions, edge_color="#94a3b8",
                           arrowsize=18, width=1.7,
                           connectionstyle="arc3,rad=0.10", ax=axis, node_size=node_size)
    edge_labels = {edge: data.get("label", "") for edge, data in graph.edges.items()}
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels,
                                 font_size=6.5, rotate=False, ax=axis)
    axis.set_title(f"{title}", loc="left", pad=12, fontweight="bold", color="#1e293b")
    if subtitle:
        axis.text(0, -0.10, subtitle, transform=axis.transAxes, fontsize=8, color="#475569")
    axis.axis("off")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(save_path, dpi=220, bbox_inches="tight")
    plt.close(figure)
# --------------------------------------------------------------------------- #
# evaluation driver                                                             #
# --------------------------------------------------------------------------- #

def _lane1_detail(report) -> dict:
    findings = report["lane1"]["details"]["findings"]
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    detail = report["lane1"]["details"]
    return {
        "passed": bool(report["lane1"]["passed"]),
        "n_errors": len(errors),
        "n_warnings": len(warnings),
        "errors": [{"rule": f["check"], "message": f["message"]} for f in errors],
        "warning_rules": sorted({f["check"] for f in warnings}),
        "reachable_states": len(detail["reachable_states"]),
        "states_with_terminal_path": len(detail["states_with_terminal_path"]),
    }


def _lane2_detail(report) -> dict:
    detail = report["lane2"]
    return {
        "coverage": detail["coverage"], "precision": detail["precision"],
        "combined": detail["combined_score"],
        "backend": detail["details"].get("backend", ""),
        "skipped": bool(detail["details"].get("skipped")),
    }


def _lane3_detail(report) -> dict:
    detail = report["lane3"]["details"]
    return {
        "checklist_passed": bool(report["lane3"]["checklist_passed"]),
        "checklist": detail["checklist"],
        "bias_flags": detail["bias_flags"],
        "bias_check_passed": bool(detail["bias_check_passed"]),
        "action_disparity": detail["maximum_action_count_disparity"],
        "stakeholder_coverage": detail["stakeholder_coverage"],
        "action_counts_by_player": dict(detail.get("action_profile_counts_by_player", {})),
    }


def draw_transition_graphs(case: str, model: dict, out_dir: Path) -> dict:
    """Full annotated graph + one per-depth diagram per BFS step from initial."""
    out_dir.mkdir(parents=True, exist_ok=True)
    graph = _build_graph(model)
    initials = [e["state"] for e in model.get("initial", [])]
    for node in graph:
        graph.nodes[node]["init"] = node in initials
    full = out_dir / f"full_{case}.png"
    terms = {n for n in graph if graph.nodes[n].get("terminal", False)}
    depth = {}
    for seed in initials:
        if seed in graph:
            for node, dist in nx.single_source_shortest_path_length(graph, seed).items():
                depth[node] = min(depth.get(node, dist), dist)
    max_depth = max((d for d in depth.values() if d is not None), default=0)
    _draw(graph, full, f"{case} — full transition graph",
          subtitle=f"{len(graph.nodes)} states · {len(graph.edges)} edges · "
                   f"blue=initial, orange=terminal · depth layers 0..{max_depth}")
    layers = {}
    for d in range(max_depth + 1):
        sub = _build_graph(model, depth_limit=d)
        for node in sub:
            sub.nodes[node]["init"] = node in initials
        name = f"depth_{d}.png"
        path = out_dir / name
        _draw(sub, path, f"{case} — steps up to depth {d}",
              subtitle="blue=initial, orange=terminal · edge labels show "
                       "player:action@p (one or more actions may share an edge)")
        layers[d] = name
    return {"full": full.name, "layers": layers, "max_depth": max_depth,
            "n_nodes": len(graph), "n_edges": len(graph.edges)}
def main() -> int:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    raw_refs = json.loads(REFERENCES.read_text(encoding="utf-8"))

    rows = []
    for case in REF_KEY:
        path = RUN_DIR / f"{case}.json"
        if not path.exists():
            continue
        candidate = json.loads(path.read_text(encoding="utf-8"))
        ref_v2, _ = ec.to_v2(json.loads(json.dumps(raw_refs[REF_KEY[case]])))
        report_dir = EVAL_DIR / case
        report = evaluate_world_model(
            candidate_model_path=candidate,
            ground_truth_path=ref_v2,
            save_pth=False,
            output_dir=str(report_dir),
        )
        (report_dir / "evaluation_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

        human_ids = [p["id"] for p in candidate["players"] if p.get("type") == "human"]
        acting = {p for s in candidate["states"] for p in s.get("turn", [])}
        guard_states = [s for s in candidate["states"] if s.get("terminal", False)]

        diff = feature_diff(ref_v2, candidate)
        summary_counts = {
            "matched": sum(1 for r in diff if r["status"] == "match"),
            "delta": sum(1 for r in diff if r["status"] == "delta"),
            "missing": sum(1 for r in diff if r["status"] == "missing"),
            "extra": sum(1 for r in diff if r["status"] == "extra"),
        }
        row = {
            "case": case,
            "reference": REF_KEY[case],
            "lane1": _lane1_detail(report),
            "lane1_extended": structural_metrics(candidate),
            "lane2": _lane2_detail(report),
            "lane2_feature_diff": diff,
            "lane2_feature_summary": summary_counts,
            "lane3": _lane3_detail(report),
            "lane3_extended": {
                "human_agents_present": bool(human_ids),
                "humans_act_somewhere": bool(human_ids) and all(h in acting for h in human_ids),
                "robots_act_somewhere": bool(
                    [p for p in candidate["players"] if p.get("type") == "robot"
                     and p["id"] in acting]),
                "outcome_granularity_terminal_states": len(guard_states),
            },
            "overall_passed": bool(report["overall_passed"]),
            "graph": draw_transition_graphs(case, candidate, GRAPHS_DIR / case),
        }
        rows.append(row)
        lane1 = row["lane1"]
        print(f"  {case:10} L1={'PASS' if lane1['passed'] else 'FAIL'} "
              f"({lane1['n_errors']}E/{lane1['n_warnings']}W)  "
              f"L2 cov={row['lane2']['coverage']:.3f} prec={row['lane2']['precision']:.3f} "
              f"comb={row['lane2']['combined']:.3f}  L3={row['lane3']['checklist_passed']} "
              f"overall={'PASS' if row['overall_passed'] else 'FAIL'}")

    aggregates = {
        "n_cases": len(rows),
        "lane1_pass": sum(1 for r in rows if r["lane1"]["passed"]),
        "overall_pass": sum(1 for r in rows if r["overall_passed"]),
        "lane3_checklist_pass": sum(1 for r in rows if r["lane3"]["checklist_passed"]),
        "bias_free": sum(1 for r in rows if r["lane3"]["bias_check_passed"]),
        "mean_lane2_coverage": round(
            sum(r["lane2"]["coverage"] for r in rows) / len(rows), 4),
        "mean_lane2_precision": round(
            sum(r["lane2"]["precision"] for r in rows) / len(rows), 4),
        "mean_lane2_combined": round(
            sum(r["lane2"]["combined"] for r in rows) / len(rows), 4),
        "mean_avg_entropy_bits": round(
            sum(r["lane1_extended"]["avg_distribution_entropy_bits"] or 0 for r in rows)
            / len(rows), 4),
        "mean_states": round(sum(r["lane1_extended"]["n_states"] for r in rows) / len(rows), 2),
        "graph_files": sum(len(r["graph"]["layers"]) + 1 for r in rows),
    }
    summary = {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
               "prompt": "prompts_library/zero_shot_v3_prompt.md",
               "aggregates": aggregates, "cases": rows}
    (RUN_DIR / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(rows)} cases evaluated; aggregates -> {RUN_DIR / 'evaluation_summary.json'}")
    print(f"transition graphs -> {GRAPHS_DIR} ({aggregates['graph_files']} PNG files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())