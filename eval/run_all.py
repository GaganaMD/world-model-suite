#!/usr/bin/env python3
"""Run the three evaluation lanes over the test-case bank, and self-test them.

    python -m eval.run_all              # scorecard over the bank
    python -m eval.run_all --selftest   # assert every invariant; exit 1 on failure

Lane 1 (validity) and Lane 2 (equivalence) run against the shipped reference
models — which are the ground truth, so they must all pass / be self-equivalent.
Lane 3 (ingredients) has no offline ground truth; the scorecard reports checklist
coverage of the bank and the κ utility, and real scoring is deferred to an
`LLMJudge` the user supplies.
"""
from __future__ import annotations

import copy
import sys

from eval import casebank
from eval.check import check_model
from eval.equivalence import equivalence
from eval.ingredients import KeywordJudge, cohen_kappa, score_case


# --------------------------------------------------------------------------- test utilities

def rename_model(m: dict) -> dict:
    """A behavior-preserving relabeling of states, players (and their references)."""
    m = copy.deepcopy(m)
    smap = {sid: f"z{i}" for i, sid in enumerate(m["states"])}
    pmap = {p["id"]: f"agent{i}" for i, p in enumerate(m["players"])}
    for p in m["players"]:
        p["id"] = pmap[p["id"]]
    m["initial_state"] = smap[m["initial_state"]]
    m["states"] = {
        smap[s]: ({**v, "reward": {pmap.get(k, k): x for k, x in v["reward"].items()}} if "reward" in v else v)
        for s, v in m["states"].items()
    }
    m["actions"] = {smap[s]: {pmap.get(p, p): acts for p, acts in by.items()} for s, by in m["actions"].items()}
    m["transition_probabilities"] = {
        smap[s]: {jk: {smap[t]: pr for t, pr in dist.items()} for jk, dist in tab.items()}
        for s, tab in m["transition_probabilities"].items()
    }
    if "rewards" in m:
        m["rewards"] = {
            smap[s]: {jk: {pmap.get(k, k): x for k, x in pay.items()} for jk, pay in tab.items()}
            for s, tab in m["rewards"].items()
        }
    return m


def drop_a_terminal(m: dict) -> dict:
    """Remove one terminal outcome and prune inbound edges — a real behavior change."""
    m = copy.deepcopy(m)
    term = next(s for s, v in m["states"].items() if v.get("terminal"))
    del m["states"][term]
    for s, tab in m["transition_probabilities"].items():
        for jk, dist in list(tab.items()):
            if term in dist:
                dist.pop(term)
                if dist:
                    tot = sum(dist.values())
                    for k in dist:
                        dist[k] /= tot
                else:
                    tab[jk] = {m["initial_state"]: 1.0}
    return m


# --------------------------------------------------------------------------- self-test

def selftest() -> bool:
    gt = {c.case_id: c.model for c in casebank.ground_truth_cases()}
    opens = casebank.open_cases()
    checks: list[tuple[str, bool]] = []

    def expect(label, cond):
        checks.append((label, bool(cond)))

    # Lane 1
    expect("L1: 19 ground-truth cases loaded", len(gt) == 19)
    expect("L1: every reference passes validity", all(check_model(m)["pass"] for m in gt.values()))
    broke = check_model({**copy.deepcopy(gt["game_G_7"]),
                         "transition_probabilities": {"s0": {"silent+silent": {"s99": 1.0}}}})
    expect("L1: undeclared-target mutation is caught", not broke["pass"])

    # Lane 2
    expect("L2: every reference is self-equivalent (f1=1.0)",
           all(equivalence(m, m)["equivalent"] and equivalence(m, m)["f1"] == 1.0 for m in gt.values()))
    expect("L2: renamed copy stays equivalent (f1=1.0)",
           all(equivalence(rename_model(m), m)["equivalent"] and equivalence(rename_model(m), m)["f1"] == 1.0
               for m in gt.values()))
    expect("L2: renamed copy still passes Lane 1",
           all(check_model(rename_model(m))["pass"] for m in gt.values()))
    expect("L2: dropping a terminal breaks equivalence (all cases)",
           all(not equivalence(drop_a_terminal(m), m)["equivalent"] for m in gt.values()))
    expect("L2: two different games are not equivalent",
           not equivalence(gt["game_G_7"], gt["game_G_1"])["equivalent"])

    # Lane 3
    expect("L3: 25 open cases loaded", len(opens) == 25)
    expect("L3: every open case has include+avoid items",
           all(c.should_include and c.should_not for c in opens))
    expect("L3: kappa perfect=1.0, inverted=-1.0",
           cohen_kappa([1, 0, 1], [1, 0, 1]) == 1.0 and cohen_kappa([1, 1, 0, 0], [0, 0, 1, 1]) == -1.0)

    ok = all(passed for _, passed in checks)
    print("SELF-TEST")
    for label, passed in checks:
        print(f"  [{'ok' if passed else 'XX'}] {label}")
    print("RESULT:", "ALL PASS" if ok else "FAILURES ABOVE")
    return ok


# --------------------------------------------------------------------------- scorecard

def scorecard() -> None:
    gt = casebank.ground_truth_cases()
    opens = casebank.open_cases()

    print("=" * 68)
    print("LANE 1 — mechanical validity (reference models must all pass)")
    print("=" * 68)
    npass = 0
    for c in gt:
        r = check_model(c.model)
        npass += r["pass"]
        flag = "" if r["pass"] else "   <-- " + "; ".join(f["rule"] for f in r["failures"][:3])
        print(f"  {c.case_id:16} {'pass' if r['pass'] else 'FAIL'}{flag}")
    print(f"  -> {npass}/{len(gt)} valid")

    print("\n" + "=" * 68)
    print("LANE 2 — behavioral equivalence up to renaming (reference vs itself)")
    print("=" * 68)
    for c in gt:
        r = equivalence(c.model, c.model)
        print(f"  {c.case_id:16} equivalent={r['equivalent']}  f1={r['f1']}  "
              f"(states={r['reference_states']})")
    demo = equivalence(gt[-1].model, gt[0].model)
    print(f"  cross-case sanity ({gt[-1].case_id} vs {gt[0].case_id}): "
          f"equivalent={demo['equivalent']} f1={demo['f1']}")

    print("\n" + "=" * 68)
    print("LANE 3 — ingredient checklists (open cases; needs an LLMJudge to score)")
    print("=" * 68)
    inc = sum(len(c.should_include) for c in opens)
    avo = sum(len(c.should_not) for c in opens)
    print(f"  {len(opens)} open cases  |  {inc} include items  |  {avo} avoid items")
    print(f"  avg per case: +{inc/len(opens):.1f} include, -{avo/len(opens):.1f} avoid")
    print("  scoring: supply eval.ingredients.LLMJudge(complete_fn); validate it with")
    print("  cohen_kappa against human labels before trusting its coverage/violation numbers.")


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return 0 if selftest() else 1
    scorecard()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
