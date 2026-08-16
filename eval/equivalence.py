#!/usr/bin/env python3
"""Lane 2 — behavioral equivalence of a candidate world model to a reference.

The question is *"how true is the model"* for cases that have a ground truth
(toy, game). Following Oswald et al. (2024), we score by **behavioral
equivalence up to renaming**, not by string/JSON similarity: two models are the
same game if their transition structure matches after abstracting away the names
of states, actions, and players.

Method — 1-WL colour refinement on the disjoint union of the two transition
graphs. A state's colour is refined from its ``terminal`` flag and the multiset
of its outgoing action-effects (each effect = the distribution over successor
colours), with action names dropped entirely, so action renaming is invariant by
construction and state/player renaming is invariant after refinement. On the tiny,
near-tree games in this suite WL is effectively exact.

Returns coverage / precision / F1 over state colours (partial credit: an omitted
reference state lowers coverage, an invented state lowers precision) plus boolean
verdicts for transition structure, player count, and (coarsely) rewards.

    from eval.equivalence import equivalence
    r = equivalence(candidate_model, reference_model)
"""
from __future__ import annotations

from collections import Counter


def _effects(model: dict, sid: str) -> list[dict[str, float]]:
    """The distributions leaving `sid`, one per joint action (names dropped)."""
    return [dict(dist) for dist in model["transition_probabilities"].get(sid, {}).values()]


def _refine(models: dict[str, dict]) -> dict[tuple[str, str], int]:
    """1-WL colours over the disjoint union. Keys are (tag, state_id)."""
    nodes: list[tuple[str, str]] = []
    terminal: dict[tuple, bool] = {}
    eff: dict[tuple, list[dict[tuple, float]]] = {}
    for tag, m in models.items():
        for sid, s in m["states"].items():
            node = (tag, sid)
            nodes.append(node)
            terminal[node] = bool(s.get("terminal"))
            eff[node] = [{(tag, t): p for t, p in dist.items()} for dist in _effects(m, sid)]

    colour: dict[tuple, int] = {n: (1 if terminal[n] else 0) for n in nodes}
    for _ in range(len(nodes) + 1):
        sig = {}
        for n in nodes:
            effect_sig = tuple(sorted(
                tuple(sorted((round(p, 6), colour[t]) for t, p in dist.items()))
                for dist in eff[n]
            ))
            sig[n] = (colour[n], effect_sig)
        # canonicalise signatures to small ints
        order = {s: i for i, s in enumerate(sorted(set(sig.values()), key=repr))}
        new = {n: order[sig[n]] for n in nodes}
        if len(set(new.values())) == len(set(colour.values())) and new == colour:
            break
        colour = new
    return colour


def _reward_signature(m: dict, colour: dict, tag: str) -> tuple:
    """Naming-invariant reward summary. None if the model carries no rewards.

    Values are sorted (player-renaming invariant); each payoff is tagged by the
    colour of the state it attaches to. Coarse by design — it certifies reward
    *shape*, not an exact per-player assignment.
    """
    facts = []
    for sid, s in m["states"].items():
        if "reward" in s:                                   # reward-on-arrival
            facts.append((colour[(tag, sid)], "state", tuple(sorted(s["reward"].values()))))
    for sid, table in m.get("rewards", {}).items():         # reward-on-action
        for payoff in table.values():
            facts.append((colour[(tag, sid)], "action", tuple(sorted(payoff.values()))))
    return tuple(sorted(facts)) if facts else None


def equivalence(candidate: dict, reference: dict) -> dict:
    """Behavioral-equivalence report for `candidate` against `reference`."""
    colour = _refine({"ref": reference, "cand": candidate})
    ref_colours = Counter(colour[("ref", s)] for s in reference["states"])
    cand_colours = Counter(colour[("cand", s)] for s in candidate["states"])

    matched = sum((ref_colours & cand_colours).values())
    coverage = matched / max(sum(ref_colours.values()), 1)     # recall on reference states
    precision = matched / max(sum(cand_colours.values()), 1)   # 1 - invention rate
    f1 = 0.0 if coverage + precision == 0 else 2 * coverage * precision / (coverage + precision)

    transition_equiv = (
        ref_colours == cand_colours
        and colour[("ref", reference["initial_state"])] == colour[("cand", candidate["initial_state"])]
    )
    players_match = len(reference["players"]) == len(candidate["players"])

    ref_rw = _reward_signature(reference, colour, "ref")
    cand_rw = _reward_signature(candidate, colour, "cand")
    reward_match = None if ref_rw is None and cand_rw is None else (ref_rw == cand_rw)

    equivalent = transition_equiv and players_match and reward_match in (True, None)
    return {
        "equivalent": equivalent,
        "transition_equivalent": transition_equiv,
        "players_match": players_match,
        "reward_match": reward_match,
        "coverage": round(coverage, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
        "reference_states": sum(ref_colours.values()),
        "candidate_states": sum(cand_colours.values()),
        "matched_state_classes": matched,
    }


if __name__ == "__main__":
    import json
    import sys

    from eval import casebank
    if len(sys.argv) == 3:
        cand = json.loads(open(sys.argv[1]).read())
        ref = json.loads(open(sys.argv[2]).read())
        print(json.dumps(equivalence(cand, ref), indent=2))
    else:
        gt = {c.case_id: c.model for c in casebank.ground_truth_cases()}
        print("self-equivalence (every reference vs itself, expect equivalent + f1=1.0):")
        for cid, m in gt.items():
            r = equivalence(m, m)
            print(f"  {cid:16} equivalent={r['equivalent']} f1={r['f1']}")
