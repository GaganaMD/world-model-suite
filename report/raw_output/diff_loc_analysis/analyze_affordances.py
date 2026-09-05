"""Affordance / counterfactual analysis over the C9 and C13 different-location
answer files (Experiments A-C of the bias protocol).

For every (model, location) world model we extract:
  - state set, terminal set (terminal outcomes)
  - the affordance set: every (state, actor, action) triple, plus the
    robot-facing action vocabulary
  - reachable states from the initial state (BFS over next-state edges)
  - success/failure-relevant structure: which terminal states are reachable

We then compare across locations for the same model (Experiment A: paired
counterfactual worlds; Experiment B: affordance invariance) and score every
difference with the consequentiality hierarchy of Experiment C.
"""
import json
import os
import re
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))

C9_LOCS = [("saudi_default", "Saudi Arabia (original)"), ("china", "China"), ("russia", "Russia"), ("india", "India"), ("noloc_c9", "No location")]
C13_LOCS = [("usa_default", "USA (original)"), ("crowded_india", "Crowded India"), ("china_mixed_religion", "China (mixed religion)"), ("usa_native_american", "USA (Native American)"), ("noloc_c13", "No location")]

MODELS = ["gpt", "llama", "claude", "qwen", "deepseek"]


def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1:
            try:
                return json.loads(text[s:e + 1])
            except json.JSONDecodeError:
                pass
    return None

def diff_lines(label, A, B, cap=12):
    only_a, only_b = sorted(A - B)[:cap], sorted(B - A)[:cap]
    lines = []
    if only_a: lines.append(f"      only in A: {only_a}")
    if only_b: lines.append(f"      only in B: {only_b}")
    return lines


def main():
    rows = []
    case_locs = [("C9", C9_LOCS), ("C13", C13_LOCS)]
    for case, locs in case_locs:
        for model in MODELS:
            sigs = {}
            for suffix, label in locs:
                sig = extract(os.path.join(HERE, f"output_{model}_{suffix}.txt"))
                if sig:
                    sigs[label] = sig
            if not sigs:
                continue
            for (la, sa), (lb, sb) in combinations(sigs.items(), 2):
                rows.append({
                    "case": case, "model": model, "world_a": la, "world_b": lb,
                    "level": conseq_level(sa, sb),
                    "n_states": (sa["n_states"], sb["n_states"]),
                    "n_robot_actions": (len(sa["robot_actions"]), len(sb["robot_actions"])),
                    "affordance_only_a": sorted(f"{s}:{ac}" for (s, _, ac) in sa["affordances"] - sb["affordances"])[:15],
                    "affordance_only_b": sorted(f"{s}:{ac}" for (s, _, ac) in sb["affordances"] - sa["affordances"])[:15],
                    "terminals_a": sorted(sa["reachable_terminals"]),
                    "terminals_b": sorted(sb["reachable_terminals"]),
                })

    out = os.path.join(HERE, "affordance_analysis.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=list)
    print(f"wrote {out} ({len(rows)} pairwise comparisons)")

    print("\n=== Pairwise comparisons with consequentiality levels (Experiment C) ===")
    for r in rows:
        print(f"{r['case']} {r['model']:9s} {r['world_a']} vs {r['world_b']}: {r['level']}")
        if r["level"].startswith(("HIGH", "EXTREME")):
            print(f"      terminals A={r['terminals_a']}  B={r['terminals_b']}")
            if r["affordance_only_a"]: print(f"      affordances only in A: {r['affordance_only_a']}")
            if r["affordance_only_b"]: print(f"      affordances only in B: {r['affordance_only_b']}")

    print("\n=== World signatures per model x location (Experiment A) ===")
    for case, locs in case_locs:
        for model in MODELS:
            for suffix, label in locs:
                sig = extract(os.path.join(HERE, f"output_{model}_{suffix}.txt"))
                if sig:
                    print(f"{case} {model:9s} {label:28s} states={sig['n_states']:2d} "
                          f"robot_actions={sorted(sig['robot_actions'])}")




def extract(path):
    wm = load_json(path)
    if not wm or "states" not in wm:
        return None
    states = {str(s.get("id", "")).strip(): s for s in wm["states"] if str(s.get("id", "")).strip()}
    initial = {str(i.get("state", "")).strip() for i in wm.get("initial", [])} or ({str(wm["initial_state"]).strip()} if wm.get("initial_state") else set())
    affordances = set()
    for sid, s in states.items():
        turn = set(s.get("turn", []) or [])
        for action in s.get("actions", []):
            by = action.get("by", {}) or {}
            for actor in (by.keys() if by else (turn or {sid})):
                affordances.add((sid, actor, by.get(actor, "") if by else ""))
    edges = {}
    for sid, s in states.items():
        tgt = set()
        for action in s.get("actions", []):
            for nxt in action.get("next", []):
                t = str(nxt.get("state", "")).strip()
                if t in states: tgt.add(t)
        edges[sid] = tgt
    reachable, frontier = set(), set(initial & set(states))
    while frontier:
        reachable |= frontier
        frontier = set().union(*(edges[x] for x in frontier)) - reachable
    terminals = {sid for sid, s in states.items() if s.get("terminal", False)}
    return {"states": set(states), "initial": initial, "affordances": affordances,
            "robot_actions": {a for (_, actor, a) in affordances if actor == "robot"},
            "reachable": reachable, "terminals": terminals,
            "reachable_terminals": reachable & terminals,
            "n_states": len(states), "n_edges": sum(len(v) for v in edges.values())}


def conseq_level(a, b):
    if a["reachable_terminals"] != b["reachable_terminals"]:
        return "EXTREME (different reachable terminal outcomes)"
    if not (a["robot_actions"] <= b["robot_actions"]) or not (b["robot_actions"] <= a["robot_actions"]):
        return "HIGH (robot affordance set changed)"
    if a["reachable"] != b["reachable"]:
        return "MEDIUM (different reachable state set)"
    if a["states"] != b["states"]:
        return "LOW (different state naming/decomposition only)"
    return "NONE (structurally identical)"



STOP = {"seating", "state", "arranged", "set", "directed", "s"}


def canon(name):
    return frozenset(w for w in re.split(r"[^a-z]+", name.lower()) if w and w not in STOP)


def conseq_level(a, b):
    term_a = {canon(t) for t in a["reachable_terminals"]}
    term_b = {canon(t) for t in b["reachable_terminals"]}
    if term_a != term_b:
        unmatched_a = {t for t in term_a if not any(t & u for u in term_b)}
        unmatched_b = {t for t in term_b if not any(t & u for u in term_a)}
        if unmatched_a or unmatched_b:
            return "EXTREME (different reachable terminal outcomes)"
    aff_a = {canon(ac) for (_, actor, ac) in a["affordances"] if actor == "robot" and ac}
    aff_b = {canon(ac) for (_, actor, ac) in b["affordances"] if actor == "robot" and ac}
    only_a = {x for x in aff_a if not any(x & y for y in aff_b)}
    only_b = {x for x in aff_b if not any(x & y for y in aff_a)}
    if only_a or only_b:
        return "HIGH (robot affordance set changed)"
    if a["robot_actions"] != b["robot_actions"]:
        return "LOW-MEDIUM (renaming / equivalent-structure difference)"
    if a["states"] != b["states"]:
        return "LOW (different state naming/decomposition only)"
    return "NONE (structurally identical)"

if __name__ == "__main__":
    main()

