#!/usr/bin/env python3
"""Lane 1 — mechanical validity of a generated world model.

Three tiers, run as gates: **parse** (tier 0), **structure** (tier 1, the shape in
``schema/world_model.schema.json``), **game validity** (tier 2, rules G1-G9). A
tier runs only if the previous one passed; within a tier every failure is
collected. The verdict is a single boolean — no warnings, no partial credit.

    python eval/check.py model.json          # report to stdout, exit 1 on failure
    cat model.json | python eval/check.py

As a library::

    from eval.check import check_text, check_model
    report = check_text(raw_llm_reply)

The tier-1 structural checks are implemented in pure Python (no dependency) and
mirror the JSON Schema exactly, so the checker runs anywhere. The schema file is
the declarative spec of the same contract.

Canonical schema (the test-case bank's shape)::

    players:      [ {id, description?} ]
    initial_state: "<state id>"
    states:       { id: {description, terminal, reward?: {player: number}} }
    actions:      { non-terminal id: {player: [action, ...]} }
    transition_probabilities:
                  { id: { joint_key: { target_id: prob } } }
    rewards?:     { id: { joint_key: {player: number} } }

``joint_key`` is one action per acting player joined by ``+`` in players order
(for a single acting player it is just that action). Because action names may
themselves contain ``+`` (e.g. Blotto ``0+3``), joint keys are validated by
*rebuilding* the Cartesian product from ``actions`` — never by splitting on ``+``.
"""
from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from typing import Any


TOL = 1e-3      # |Σp − 1| tolerance: probabilities may be rounded to 3-4 decimals
NATURE = "nature"   # reserved chance actor; a state where it "acts" is a chance node
                    # (exempt from player-declaration and reward rules)


# --------------------------------------------------------------------------- report

def fail(rule: str, where: str, detail: str) -> dict[str, str]:
    return {"rule": rule, "where": where, "detail": detail}


def report(failures: list[dict], skipped: list[str], counts: dict | None) -> dict:
    return {"pass": not failures, "failures": failures, "skipped": skipped, "counts": counts}


def _dups(items) -> list:
    return sorted({i for i, n in Counter(items).items() if n > 1})


def _names(items) -> str:
    return ", ".join(str(i) for i in items)


# --------------------------------------------------------------------------- tier 0

def parse(raw: str) -> tuple[Any, list[dict]]:
    """The reply must be exactly one JSON object. Nothing is stripped."""
    try:
        model = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [fail("parse", "reply", f"not valid JSON: {exc}{_hint(raw.strip())}")]
    if not isinstance(model, dict):
        return None, [fail("parse", "reply", f"top level is a {type(model).__name__}, expected an object")]
    return model, []


def _hint(text: str) -> str:
    if text.startswith("```"):
        return "; the reply is wrapped in a code fence"
    if "{" in text and not text.startswith("{"):
        return "; there is text before the JSON object"
    if text.endswith("```") or (text.endswith((".", "!")) and "}" in text):
        return "; there is text after the JSON object"
    return ""


# --------------------------------------------------------------------------- tier 1 (structure)

def _is_str(x): return isinstance(x, str) and x != ""
def _is_num(x): return isinstance(x, (int, float)) and not isinstance(x, bool)


def check_structure(m: Any) -> list[dict]:
    """Pure-Python mirror of world_model.schema.json. Collects every shape error."""
    f: list[dict] = []
    top = {"players", "initial_state", "states", "actions", "transition_probabilities", "rewards"}
    for k in m:
        if k not in top:
            f.append(fail("schema", k, "unknown top-level key"))
    for req in ("players", "initial_state", "states", "actions", "transition_probabilities"):
        if req not in m:
            f.append(fail("schema", req, "missing required key"))

    players = m.get("players")
    if not isinstance(players, list) or not players:
        f.append(fail("schema", "players", "must be a non-empty array"))
    else:
        for i, p in enumerate(players):
            if not isinstance(p, dict) or not _is_str(p.get("id")):
                f.append(fail("schema", f"players[{i}]", "must be an object with a non-empty 'id'"))
            elif set(p) - {"id", "description"}:
                f.append(fail("schema", f"players[{i}]", f"unknown key(s): {_names(set(p) - {'id', 'description'})}"))

    if not _is_str(m.get("initial_state")):
        f.append(fail("schema", "initial_state", "must be a non-empty string"))

    states = m.get("states")
    if not isinstance(states, dict) or not states:
        f.append(fail("schema", "states", "must be a non-empty object"))
    else:
        for sid, s in states.items():
            w = f"states.{sid}"
            if not isinstance(s, dict):
                f.append(fail("schema", w, "must be an object")); continue
            if set(s) - {"description", "terminal", "reward"}:
                f.append(fail("schema", w, f"unknown key(s): {_names(set(s) - {'description', 'terminal', 'reward'})}"))
            if not isinstance(s.get("description"), str):
                f.append(fail("schema", f"{w}.description", "must be a string"))
            if not isinstance(s.get("terminal"), bool):
                f.append(fail("schema", f"{w}.terminal", "must be a boolean"))
            if "reward" in s:
                _check_payoff(f, f"{w}.reward", s["reward"])

    _check_actions(f, m.get("actions"))
    _check_tp(f, m.get("transition_probabilities"))
    if "rewards" in m:
        _check_rewards(f, m["rewards"])
    return f


def _check_payoff(f, where, r):
    if not isinstance(r, dict) or not r:
        f.append(fail("schema", where, "must be a non-empty object of player -> number")); return
    for pid, v in r.items():
        if not _is_num(v):
            f.append(fail("schema", f"{where}.{pid}", "must be a number"))


def _check_actions(f, actions):
    if not isinstance(actions, dict):
        f.append(fail("schema", "actions", "must be an object")); return
    for sid, by in actions.items():
        w = f"actions.{sid}"
        if not isinstance(by, dict) or not by:
            f.append(fail("schema", w, "must be a non-empty object of player -> [actions]")); continue
        for pid, acts in by.items():
            if not isinstance(acts, list) or not acts or not all(_is_str(a) for a in acts):
                f.append(fail("schema", f"{w}.{pid}", "must be a non-empty array of action strings"))


def _check_tp(f, tp):
    if not isinstance(tp, dict):
        f.append(fail("schema", "transition_probabilities", "must be an object")); return
    for sid, table in tp.items():
        w = f"transition_probabilities.{sid}"
        if not isinstance(table, dict) or not table:
            f.append(fail("schema", w, "must be a non-empty object of joint_key -> distribution")); continue
        for jk, dist in table.items():
            if not isinstance(dist, dict) or not dist:
                f.append(fail("schema", f"{w}.{jk}", "must be a non-empty object of target_state -> prob")); continue
            for tgt, p in dist.items():
                if not _is_num(p):
                    f.append(fail("schema", f"{w}.{jk}.{tgt}", "probability must be a number"))


def _check_rewards(f, rewards):
    if not isinstance(rewards, dict):
        f.append(fail("schema", "rewards", "must be an object")); return
    for sid, table in rewards.items():
        w = f"rewards.{sid}"
        if not isinstance(table, dict):
            f.append(fail("schema", w, "must be an object of joint_key -> payoff")); continue
        for jk, payoff in table.items():
            _check_payoff(f, f"{w}.{jk}", payoff)


# --------------------------------------------------------------------------- tier 2 (game validity)

def _acting(m, sid) -> list[str]:
    """Actors in `sid`, in join order: declared players (players order), then `nature`."""
    by = m["actions"].get(sid, {})
    order = [p["id"] for p in m["players"] if p["id"] in by]
    if NATURE in by and NATURE not in order:
        order.append(NATURE)
    return order


def _expected_joint_keys(m, sid) -> set[str]:
    by = m["actions"].get(sid, {})
    acting = _acting(m, sid)
    if not acting:
        return set()
    combos = itertools.product(*[by[p] for p in acting])
    return {"+".join(combo) for combo in combos}


def check_rules(m: dict) -> tuple[list[dict], list[str]]:
    """Tier-2 rules with gating. Returns (failures, skipped-rule-ids)."""
    fails: list[dict] = []
    skipped: list[str] = []
    players = m["players"]
    states = m["states"]
    actions = m["actions"]
    tp = m["transition_probabilities"]
    rewards = m.get("rewards", {})
    pids = [p["id"] for p in players]
    sids = set(states)
    terminals = {sid for sid, s in states.items() if s.get("terminal")}

    # G1 — player ids unique
    if d := _dups(pids):
        fails.append(fail("G1", "players", f"duplicate player id(s): {_names(d)}"))

    # G2 — references resolve (initial_state, action/tp/reward keys, targets, players)
    refs_ok = True

    def bad(rule, where, detail):
        nonlocal refs_ok
        refs_ok = False
        fails.append(fail(rule, where, detail))

    if m["initial_state"] not in sids:
        bad("G2", "initial_state", f"'{m['initial_state']}' is not a declared state")
    for sid in actions:
        if sid not in sids:
            bad("G2", f"actions.{sid}", "not a declared state")
    for sid in tp:
        if sid not in sids:
            bad("G2", f"transition_probabilities.{sid}", "not a declared state")
    for sid in rewards:
        if sid not in sids:
            bad("G2", f"rewards.{sid}", "not a declared state")
    for sid, by in actions.items():
        for pid in by:
            if pid not in pids and pid != NATURE:
                bad("G2", f"actions.{sid}.{pid}", "not a declared player")
    for sid, table in tp.items():
        for jk, dist in table.items():
            for tgt in dist:
                if tgt not in sids:
                    bad("G2", f"transition_probabilities.{sid}.{jk}", f"target '{tgt}' is not a declared state")
    for sid, s in states.items():
        for pid in (s.get("reward") or {}):
            if pid not in pids:
                bad("G2", f"states.{sid}.reward", f"'{pid}' is not a declared player")
    for sid, table in rewards.items():
        for jk, payoff in table.items():
            for pid in payoff:
                if pid not in pids:
                    bad("G2", f"rewards.{sid}.{jk}", f"'{pid}' is not a declared player")

    # G3 — terminal shape
    shape_ok = True
    for sid, s in states.items():
        term = s.get("terminal")
        has_actions = sid in actions
        has_tp = sid in tp
        if term and (has_actions or has_tp):
            shape_ok = False
            extra = [k for k, has in (("actions", has_actions), ("transition_probabilities", has_tp)) if has]
            fails.append(fail("G3", f"states.{sid}", f"terminal state has {_names(extra)}"))
        if not term and not (has_actions and has_tp):
            shape_ok = False
            missing = [k for k, has in (("actions", has_actions), ("transition_probabilities", has_tp)) if not has]
            fails.append(fail("G3", f"states.{sid}", f"non-terminal state has no {_names(missing)}"))

    # G4 — distributions: positive, unique target (dict-enforced), sum to 1
    for sid, table in tp.items():
        for jk, dist in table.items():
            if oor := [p for p in dist.values() if not 0 < p <= 1]:
                fails.append(fail("G4", f"transition_probabilities.{sid}.{jk}", f"prob outside (0,1]: {_names(oor)}"))
            total = sum(dist.values())
            if abs(total - 1) > TOL:
                fails.append(fail("G4", f"transition_probabilities.{sid}.{jk}", f"probabilities sum to {total:g}, not 1"))

    # G5 — action lists have no duplicate names
    for sid, by in actions.items():
        for pid, acts in by.items():
            if d := _dups(acts):
                fails.append(fail("G5", f"actions.{sid}.{pid}", f"duplicate action(s): {_names(d)}"))

    # G6 — joint-action completeness (needs refs+shape). tp keys == Cartesian product; rewards keys match too.
    if not refs_ok or not shape_ok:
        skipped.append("G6")
    else:
        for sid, s in states.items():
            if s.get("terminal"):
                continue
            expected = _expected_joint_keys(m, sid)
            present = set(tp.get(sid, {}))
            if missing := sorted(expected - present):
                fails.append(fail("G6", f"transition_probabilities.{sid}",
                                  f"missing joint action(s): {_names(missing[:6])}"
                                  + (f" (+{len(missing) - 6} more)" if len(missing) > 6 else "")))
            if extra := sorted(present - expected):
                fails.append(fail("G6", f"transition_probabilities.{sid}",
                                  f"joint action(s) not in the action product: {_names(extra[:6])}"))
            if sid in rewards:
                rkeys = set(rewards[sid])
                if diff := sorted(expected ^ rkeys):
                    fails.append(fail("G6", f"rewards.{sid}",
                                      f"reward keys do not match joint actions: {_names(diff[:6])}"))

    # G7 — reward well-formedness: exactly the acting players get a payoff (when rewards given)
    for sid, table in rewards.items():
        if sid not in states:
            continue
        acting = set(_acting(m, sid)) - {NATURE}   # nature never receives a payoff
        for jk, payoff in table.items():
            if acting and set(payoff) != acting:
                miss, extra = acting - set(payoff), set(payoff) - acting
                bits = [f"{lbl} {_names(sorted(x))}" for lbl, x in (("missing", miss), ("extra", extra)) if x]
                fails.append(fail("G7", f"rewards.{sid}.{jk}", f"payoff players != acting {sorted(acting)}: {'; '.join(bits)}"))

    # G8 — every state reachable from initial_state
    if not refs_ok:
        skipped.append("G8")
    else:
        edges = {sid: set() for sid in states}
        for sid, table in tp.items():
            for dist in table.values():
                edges[sid] |= set(dist)
        seen = _reach({m["initial_state"]}, edges)
        if orphan := sorted(sids - seen):
            fails.append(fail("G8", "states", f"unreachable from initial_state: {_names(orphan)}"))

    # G9 — a terminal exists and every state can reach one
    if not refs_ok:
        skipped.append("G9")
    else:
        back = {sid: set() for sid in states}
        for sid, table in tp.items():
            for dist in table.values():
                for tgt in dist:
                    if tgt in back:
                        back[tgt].add(sid)
        if not terminals:
            fails.append(fail("G9", "states", "no terminal state"))
        elif stuck := sorted(sids - _reach(terminals, back)):
            fails.append(fail("G9", "states", f"no path to a terminal from: {_names(stuck)}"))

    return fails, skipped


def _reach(seeds, edges) -> set:
    seen, frontier = set(seeds), list(seeds)
    while frontier:
        for nxt in edges.get(frontier.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def _counts(m: dict) -> dict:
    return {
        "players": len(m["players"]),
        "states": len(m["states"]),
        "terminal": sum(1 for s in m["states"].values() if s.get("terminal")),
        "joint_actions": sum(len(t) for t in m["transition_probabilities"].values()),
    }


# --------------------------------------------------------------------------- entry points

RULE_IDS = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]


def check_model(model: Any) -> dict:
    """Tiers 1-2 over an already-parsed object."""
    if struct := check_structure(model):
        return report(struct, list(RULE_IDS), None)
    fails, skipped = check_rules(model)
    return report(fails, skipped, _counts(model))


def check_text(raw: str) -> dict:
    """Tiers 0-2 over a raw reply."""
    model, failures = parse(raw)
    if failures:
        return report(failures, ["schema"] + list(RULE_IDS), None)
    return check_model(model)


def main(argv: list[str]) -> int:
    raw = sys.stdin.read() if not argv else __import__("pathlib").Path(argv[0]).read_text()
    result = check_text(raw)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
