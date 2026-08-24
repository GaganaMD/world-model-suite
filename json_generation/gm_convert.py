"""
gm_convert_v2.py: Lane 2 adapter 
=======================================================
Converts a world model in the team's current schema (prompts_library/zero_shot_v2_prompt.md,
validated by json_generation/mechanical_checks.py) into the format expected by
`game_matching`, so a generated model can be compared to a reference model *up to renaming*.

evaluate LLM outputs by comparing them against
algorithmically rolled-out state-action JSON, rather than against ground-truth Python code.

v2 schema (source)                         game_matching (target)
----------------------------------------   ---------------------------------------
players: [{id, type, ...}]                  players: ["id", ...]
initial: [{state, p}, ...]  (a PRIOR)       root: single state  -> see note below
states:  [{id, desc, terminal,              states: {id: {...}}
           turn: [...], actions: [...]}]
actions: [{by: {p: a}, next: [{state,p}]}]  transitions: [{profile: {p:a}, next: {s: p}}]
terminal state: no turn/actions             terminal: true + payoffs

Three schema gaps had to be bridged, each is recorded in the returned `_conversion` block
rather than hidden, so every score is reported together with the assumptions behind it.

1. PRIOR OVER INITIAL STATES (new in v2: the exact initial state is
   almost always uncertain because the situation description leaves parts of the state
   open). game_matching wants a single root. We add a synthetic root whose single joint
   action leads to the prior distribution. Semantics are preserved exactly: the chance
   over openings becomes a chance transition. The synthetic root is excluded from the
   readable state map so it never shows up as a "matched" state.

2. CYCLES: game_matching requires a DAG, our models have self-loops (a wait action that
   returns to the same state). "unrolling a finite horizon seems like the pragmatic choice". 
   State `s` at depth `d` becomes `s@d`.
   ASSUMPTION: behaviour beyond `horizon` steps is not represented.

3. TERMINAL PAYOFFS: game_matching requires payoffs on every terminal, our schema has no
   rewards. 
   ASSUMPTION: all endings treated as equally valuable. Acceptable only
   because Lane 2 compares *structure*.

Note on terminality: Being terminal is not a feature of the real world but
a feature of the model. There is no ground truth about being modelled as terminal. So a
terminal/non-terminal disagreement between two models is a modelling difference, not an
error. `horizon` is therefore applied to BOTH models being compared, which puts them on the
same evaluation horizon and stops one model being penalised for stopping earlier.
"""

from __future__ import annotations
from typing import Dict, List, Optional

SYNTHETIC_ROOT = "__root__"
SYNTHETIC_PLAYER_ACTION = "__start__"


# ─────────────────────────────────────────────────────────── reading the v2 schema

def player_ids(model: dict) -> List[str]:
    return [p["id"] for p in model.get("players", [])]


def states_by_id(model: dict) -> Dict[str, dict]:
    return {s["id"]: s for s in model.get("states", [])}



def _acts_in_order(state: dict, player: str) -> List[str]:
    """Actions of `player` at this state, in first-appearance order (not sorted:
    sorting makes the action list order depend on the names, which must not
    influence a renaming-invariant comparison)."""
    seen, out = set(), []
    for entry in state.get("actions", []) or []:
        a = entry.get("by", {}).get(player)
        if a is not None and a not in seen:
            seen.add(a); out.append(a)
    return out


def is_terminal(state: dict) -> bool:
    return bool(state.get("terminal", False))


def successors(state: dict) -> List[str]:
    out = []
    for entry in state.get("actions", []) or []:
        for nxt in entry.get("next", []) or []:
            out.append(nxt["state"])
    return out


def has_cycle(model: dict) -> bool:
    """True if the transition graph contains any cycle (including self-loops)."""
    S = states_by_id(model)
    colour: Dict[str, int] = {}

    def visit(sid: str) -> bool:
        colour[sid] = 0                       # visiting
        for nxt in successors(S.get(sid, {})):
            if colour.get(nxt) == 0:
                return True
            if nxt not in colour and nxt in S and visit(nxt):
                return True
        colour[sid] = 1                       # done
        return False

    for sid in S:
        if sid not in colour and visit(sid):
            return True
    return False


def natural_horizon(model: dict, cap: int = 12) -> int:
    """Default unrolling depth: any simple path visits each state at most once."""
    return min(max(len(model.get("states", [])), 2), cap)


# ─────────────────────────────────────────────────────────────────── conversion

def to_game_matching(
    model: dict,
    horizon: Optional[int] = None,
    unroll: str = "auto",
    default_payoff: float = 0.0,
) -> dict:
    """Convert a v2-schema model into a `game_matching` game dict.

    unroll: "auto" (only if cyclic) | "always" | "never"
    """
    players = player_ids(model)
    S = states_by_id(model)
    prior = model.get("initial", [])
    if not prior:
        raise ValueError("model has no 'initial' distribution")

    cyclic = has_cycle(model)
    do_unroll = (unroll == "always") or (unroll == "auto" and cyclic)
    H = horizon if horizon is not None else natural_horizon(model)
    multi_start = len(prior) > 1

    out: Dict[str, dict] = {}
    truncated: List[str] = []

    def terminal_node(src: str) -> dict:
        return {"terminal": True,
                "payoffs": {p: float(default_payoff) for p in players},
                "_src": src}

    def transitions_of(state: dict, depth: Optional[int]) -> List[dict]:
        rows = []
        for entry in state.get("actions", []) or []:
            nxt = {}
            for e in entry.get("next", []) or []:
                target = f"{e['state']}@{depth + 1}" if depth is not None else e["state"]
                nxt[target] = e["p"]
            rows.append({"profile": dict(entry["by"]), "next": nxt})
        return rows

    if not do_unroll:
        for sid, sd in S.items():
            if is_terminal(sd):
                out[sid] = terminal_node(sid)
            else:
                out[sid] = {"actions": {p: _acts_in_order(sd, p) for p in sd.get("turn", [])},
                            "transitions": transitions_of(sd, None),
                            "_src": sid}
        root = prior[0]["state"]
    else:
        def node(sid: str, d: int) -> str:
            return f"{sid}@{d}"

        frontier = [(e["state"], 0) for e in prior]
        seen = set()
        while frontier:
            sid, d = frontier.pop()
            if (sid, d) in seen or sid not in S:
                continue
            seen.add((sid, d))
            name, sd = node(sid, d), S[sid]

            if is_terminal(sd):
                out[name] = terminal_node(sid)
                continue
            if d >= H:
                out[name] = terminal_node(sid)
                out[name]["_truncated"] = True
                truncated.append(name)
                continue

            out[name] = {"actions": {p: _acts_in_order(sd, p) for p in sd.get("turn", [])},
                         "transitions": transitions_of(sd, d),
                         "_src": sid}
            for e in sd.get("actions", []) or []:
                for n in e.get("next", []) or []:
                    frontier.append((n["state"], d + 1))
        root = node(prior[0]["state"], 0)

    # A prior over openings needs a synthetic root, because game_matching takes one root.
    if multi_start:
        first = players[0] if players else "p0"
        out[SYNTHETIC_ROOT] = {
            "actions": {first: [SYNTHETIC_PLAYER_ACTION]},
            "transitions": [{
                "profile": {first: SYNTHETIC_PLAYER_ACTION},
                "next": {(f"{e['state']}@0" if do_unroll else e["state"]): e["p"] for e in prior},
            }],
            "_src": SYNTHETIC_ROOT,
        }
        root = SYNTHETIC_ROOT

    assumptions = []
    if do_unroll:
        assumptions.append(f"unrolled to horizon {H}; behaviour beyond {H} steps not represented")
    if truncated:
        assumptions.append(f"{len(truncated)} state(s) truncated into terminals at the horizon")
    if multi_start:
        assumptions.append(f"prior over {len(prior)} initial states modelled as a chance move from a synthetic root")
    assumptions.append(f"terminal payoffs defaulted to {default_payoff} (structure-only comparison)")

    return {"players": players, "root": root, "states": out,
            "_conversion": {"source_was_cyclic": cyclic, "unrolled": do_unroll,
                            "horizon": H if do_unroll else None,
                            "n_states_source": len(S), "n_states_converted": len(out),
                            "n_truncated_states": len(truncated),
                            "prior_over_initial_states": multi_start,
                            "assumptions": assumptions}}


def strip_private(game: dict) -> dict:
    """Drop bookkeeping keys so the dict is exactly what game_matching expects."""
    return {"players": game["players"], "root": game["root"],
            "states": {s: {k: v for k, v in sd.items() if not k.startswith("_")}
                       for s, sd in game["states"].items()}}
