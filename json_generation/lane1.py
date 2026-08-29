"""
Lane 1: mechanical checks 
===========================================
Fully automated structural-validity checks that need no ground truth: they run on any
world model in the v2 schema (players / initial(list) / states(list) with turn,by,next).

Findings map to the failure taxonomy: Cat1 invalid, Cat2 schema, Cat3 mechanical.

"""
from __future__ import annotations
from itertools import product

FAIL, WARN = "FAIL", "WARN"


class F:
    def __init__(self, check, sev, cat, msg):
        self.check, self.sev, self.cat, self.msg = check, sev, cat, msg
    def __repr__(self):
        return f"[{self.sev}] ({self.cat}) {self.check}: {self.msg}"


def _states(m):
    return {s["id"]: s for s in m.get("states", [])}


def check_v2(model, prob_tol=1e-3):
    # prob_tol=1e-3 tolerates rounding from writing probabilities to 3-4 decimals
    # (e.g. 0.4167+0.4167+0.1667 = 1.0001, or 0.333*3 = 0.999) while still catching
    # any real error: the subtlest meaningful mistake (0.99 vs 1.0) is 10x this bound.
    # Per Jobst's note (be tolerant to numerical error up to some epsilon).
    f = []
    # ---- Cat 2: schema shape ----
    for key in ("players", "initial", "states"):
        if key not in model:
            f.append(F("SCHEMA-keys", FAIL, "Cat2", f"missing top-level '{key}'"))
    if f:
        return f
    if not isinstance(model["players"], list) or not model["players"]:
        f.append(F("SCHEMA-players", FAIL, "Cat2", "'players' must be a non-empty list"))
    if not isinstance(model["initial"], list) or not model["initial"]:
        f.append(F("SCHEMA-initial", FAIL, "Cat2", "'initial' must be a non-empty list (a prior over states)"))
    if not isinstance(model["states"], list) or not model["states"]:
        f.append(F("SCHEMA-states", FAIL, "Cat2", "'states' must be a non-empty list"))
    if f:
        return f

    pids = [p["id"] for p in model["players"]]
    if len(set(pids)) != len(pids):
        f.append(F("G1-dup-player", FAIL, "Cat2", f"duplicate player ids: {pids}"))
    S = _states(model)
    if len(S) != len(model["states"]):
        f.append(F("G1-dup-state", FAIL, "Cat2", "duplicate state ids"))

    # ---- Cat 3: mechanics ----
    # initial prior: valid distribution over existing states, positive probs
    itot = 0.0
    for e in model["initial"]:
        if e["state"] not in S:
            f.append(F("MECH-initial", FAIL, "Cat3", f"initial references undeclared state '{e['state']}'"))
        if e["p"] <= 0:
            f.append(F("G4-initial-pos", FAIL, "Cat3", f"initial prob for '{e['state']}' must be positive, got {e['p']}"))
        itot += e["p"]
    if abs(itot - 1.0) > prob_tol:
        f.append(F("G4-initial-sum", FAIL, "Cat3", f"initial prior sums to {itot}, not 1"))

    reachable, frontier = set(), [e["state"] for e in model["initial"]]

    for sid, sd in S.items():
        terminal = bool(sd.get("terminal", False))
        turn = sd.get("turn", [])
        actions = sd.get("actions", [])
        if terminal:
            if turn or actions:
                f.append(F("G5-terminal", FAIL, "Cat3", f"terminal state '{sid}' has turn/actions"))
            continue
        # non-terminal must have both
        if not turn:
            f.append(F("G5-nonterminal", FAIL, "Cat3", f"non-terminal '{sid}' has no 'turn'"))
        if not actions:
            f.append(F("G5-nonterminal", FAIL, "Cat3", f"non-terminal '{sid}' has no actions (dead end)"))
        for p in turn:
            if p not in pids:
                f.append(F("G6-turn", FAIL, "Cat3", f"state '{sid}': turn names undeclared player '{p}'"))
        # each action entry: by covers exactly the turn players, next is a valid positive distribution to real states
        seen_profiles = set()
        for a in actions:
            by = a.get("by", {})
            if set(by.keys()) != set(turn):
                f.append(F("G7-profile", FAIL, "Cat3",
                           f"state '{sid}': action 'by' {set(by)} != turn {set(turn)} (every acting player needs an action)"))
            key = tuple(sorted(by.items()))
            if key in seen_profiles:
                f.append(F("G8-dup-profile", FAIL, "Cat3", f"state '{sid}': duplicate action profile {by}"))
            seen_profiles.add(key)
            nxt = a.get("next", [])
            tot = 0.0
            for n in nxt:
                if n["state"] not in S:
                    f.append(F("MECH-next", FAIL, "Cat3", f"state '{sid}': transition to undeclared state '{n['state']}'"))
                if n["p"] <= 0:
                    f.append(F("G4-pos", FAIL, "Cat3", f"state '{sid}' profile {by}: prob for '{n['state']}' must be positive (no zeros), got {n['p']}"))
                tot += n["p"]
                reachable  # noqa
            if abs(tot - 1.0) > prob_tol:
                f.append(F("G4-sum", FAIL, "Cat3", f"state '{sid}' profile {by}: successor probs sum to {tot}, not 1"))
        # completeness: every combination of the turn players' actions should appear
        if turn:
            per_player = {p: sorted({a["by"][p] for a in actions if p in a.get("by", {})}) for p in turn}
            expected = {tuple(sorted(dict(zip(turn, combo)).items())) for combo in product(*[per_player[p] for p in turn])}
            actual = {tuple(sorted(a["by"].items())) for a in actions}
            for miss in expected - actual:
                f.append(F("G7-incomplete", FAIL, "Cat3", f"state '{sid}': missing action profile {dict(miss)}"))

    # G11: every player must act somewhere
    acting = set()
    for sd in S.values():
        for p in sd.get("turn", []):
            acting.add(p)
    for p in pids:
        if p not in acting:
            f.append(F("G11-idle-player", WARN, "Cat3", f"player '{p}' never appears in any 'turn'"))

    # G9 reachability (BFS) + G10 every state can reach a terminal
    seen = set()
    while frontier:
        s = frontier.pop()
        if s in seen or s not in S:
            continue
        seen.add(s)
        for a in S[s].get("actions", []):
            for n in a.get("next", []):
                frontier.append(n["state"])
    for sid in S:
        if sid not in seen:
            f.append(F("G9-unreachable", FAIL, "Cat3", f"state '{sid}' unreachable from initial"))
    # can each state reach a terminal?
    term = {sid for sid, sd in S.items() if sd.get("terminal")}
    if not term:
        f.append(F("G10-no-terminal", FAIL, "Cat3", "no terminal state exists"))
    else:
        # backward reachability from terminals
        rev = {sid: set() for sid in S}
        for sid, sd in S.items():
            for a in sd.get("actions", []):
                for n in a.get("next", []):
                    if n["state"] in rev:
                        rev[n["state"]].add(sid)
        can_reach, stack = set(term), list(term)
        while stack:
            s = stack.pop()
            for pre in rev.get(s, ()):
                if pre not in can_reach:
                    can_reach.add(pre); stack.append(pre)
        for sid in S:
            if sid not in can_reach:
                f.append(F("G10-no-path-to-terminal", FAIL, "Cat3", f"state '{sid}' has no path to any terminal"))
    return f


def run_lane1(model, name="model"):
    findings = check_v2(model)
    fails = [x for x in findings if x.sev == FAIL]
    return {"name": name, "verdict": "PASS" if not fails else "FAIL",
            "n_fail": len(fails), "n_warn": len(findings) - len(fails), "findings": findings}


def print_lane1(r):
    print(f"{r['name']:42} {r['verdict']:4}  ({r['n_fail']} fail, {r['n_warn']} warn)")
    for x in r["findings"]:
        print("      ", x)
