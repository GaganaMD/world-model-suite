#!/usr/bin/env python3
"""Stage-1 checker for generated world models — see ``docs/evaluation.md``.

Three tiers, run as gates: parse (tier 0), JSON Schema (tier 1, from
``schema/world_model.schema.json``), game validity (tier 2, rules G1-G11). A tier
runs only if the previous one passed; within a tier every failure is collected.
The verdict is a single boolean — no warnings, no partial credit.

    python eval/check.py model.json          # report to stdout, exit 1 if it fails
    cat model.json | python eval/check.py

As a library::

    from check import check_text, check_model
    report = check_text(raw_llm_reply)

Provenance — situation id, sample index, model, prompt hash — is the caller's
job: merge it into the returned report.
"""
from __future__ import annotations

import itertools
import json
import pathlib
import re
import sys
from collections import Counter
from functools import cached_property, lru_cache
from typing import Any, Callable, Iterable, Iterator

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "world_model.schema.json"

ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")   # G2: short, lowercase, snake_case
TOL = 1e-6                                  # G4: |Σp − 1| tolerance, for float arithmetic

Finding = tuple[str, str]                   # (where, detail) — the rule id is added by run()


# --------------------------------------------------------------------------- helpers

def duplicates(items: Iterable) -> list:
    """The items appearing more than once, sorted."""
    return sorted({i for i, n in Counter(items).items() if n > 1})


def names(items: Iterable) -> str:
    return ", ".join(str(i) for i in items)


def joint(combos: list[tuple], limit: int = 3) -> str:
    """``{bot: wait, res: leave}`` for the first few joint actions."""
    shown = ", ".join("{" + ", ".join(f"{p}: {a}" for p, a in c) + "}" for c in combos[:limit])
    return shown + (f" (+{len(combos) - limit} more)" if len(combos) > limit else "")


def path(parts: Iterable) -> str:
    """``players[0].id`` from a jsonschema error path."""
    out = ""
    for part in parts:
        out += f"[{part}]" if isinstance(part, int) else (f".{part}" if out else str(part))
    return out or "model"


def reachable(seeds: Iterable[str], edges: dict[str, set[str]]) -> set[str]:
    """Every node reachable from `seeds` by following `edges`."""
    seen, frontier = set(seeds), list(seeds)
    while frontier:
        for nxt in edges.get(frontier.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return seen


def product_diff(turn: list[str], actions: list[dict]) -> tuple[dict, set, list, list]:
    """One state's joint-action table against the Cartesian product it should be.

    Returns each mover's action set, the full product, the combinations missing
    from `actions`, and the ones appearing more than once.
    """
    sets = {p: sorted({e["by"][p] for e in actions}) for p in sorted(turn)}
    product = {tuple(sorted(zip(sets, combo))) for combo in itertools.product(*sets.values())}
    seen = Counter(tuple(sorted(e["by"].items())) for e in actions)
    return sets, product, sorted(product - set(seen)), sorted(c for c, n in seen.items() if n > 1)


# --------------------------------------------------------------------------- the model

class Model:
    """A tier-1-valid world model, plus the views the rules share.

    Every property is safe to read once the schema has passed: keys are present
    and correctly typed. Nothing here assumes the model is *valid* — that is what
    the rules decide.
    """

    def __init__(self, raw: dict):
        self.raw = raw
        self.players: list[dict] = raw["players"]
        self.states: list[dict] = raw["states"]
        self.initial: list[dict] = raw["initial"]

    @cached_property
    def player_ids(self) -> list[str]:
        return [p["id"] for p in self.players]

    @cached_property
    def state_ids(self) -> list[str]:
        return [s["id"] for s in self.states]

    @cached_property
    def declared(self) -> set[str]:
        return set(self.state_ids)

    @cached_property
    def terminals(self) -> set[str]:
        return {s["id"] for s in self.states if s["terminal"]}

    @cached_property
    def items(self) -> list[tuple[str, dict]]:
        """(where, state) for every state."""
        return [(f"states[{i}]", s) for i, s in enumerate(self.states)]

    @cached_property
    def entries(self) -> list[tuple[str, dict]]:
        """(where, action entry) for every joint action anywhere in the model."""
        return [(f"{w}.actions[{i}]", e)
                for w, s in self.items for i, e in enumerate(s.get("actions") or [])]

    @cached_property
    def moves(self) -> list[tuple[str, list[str], list[dict]]]:
        """(where, turn, actions) for every non-terminal state that declares both."""
        return [(w, s["turn"], s["actions"]) for w, s in self.items
                if not s["terminal"] and s.get("turn") and s.get("actions")]

    @cached_property
    def tables(self) -> list[tuple[str, list[str], list[dict]]]:
        """The `moves` whose every `by` names exactly the players in `turn`.

        Anywhere else the joint-action table cannot be read, and G7 has said so.
        """
        return [(w, t, a) for w, t, a in self.moves if all(set(e["by"]) == set(t) for e in a)]

    @cached_property
    def dists(self) -> list[tuple[str, list[dict]]]:
        """(where, distribution) for `initial` and every action's `next`."""
        return [("initial", self.initial)] + [(f"{w}.next", e["next"]) for w, e in self.entries]

    @cached_property
    def edges(self) -> dict[str, set[str]]:
        """State id -> the states it can move to. Meaningful once G3 has passed."""
        out: dict[str, set[str]] = {sid: set() for sid in self.state_ids}
        for w, s in self.items:
            for e in s.get("actions") or []:
                out[s["id"]] |= {n["state"] for n in e["next"]}
        return out

    @cached_property
    def back_edges(self) -> dict[str, set[str]]:
        """The same graph reversed, for asking what can reach a terminal state."""
        out: dict[str, set[str]] = {sid: set() for sid in self.state_ids}
        for src, dsts in self.edges.items():
            for dst in dsts:
                if dst in out:
                    out[dst].add(src)
        return out

    @cached_property
    def acting(self) -> set[str]:
        """Every player who appears in some `turn`."""
        return {p for _, s in self.items for p in (s.get("turn") or [])}

    @cached_property
    def counts(self) -> dict[str, int]:
        return {
            "players": len(self.players),
            "states": len(self.states),
            "terminal": sum(1 for s in self.states if s["terminal"]),
            "joint_actions": len(self.entries),
        }


# --------------------------------------------------------------------------- tier 2

CHECKS: list[Callable[[Model], Iterator[Finding]]] = []


def rule(rid: str, needs: str = ""):
    """Register a tier-2 rule.

    `needs` names a rule whose failure leaves this one undecidable; the runner
    then reports this rule as skipped rather than passed.
    """
    def register(fn):
        fn.rule, fn.needs = rid, {needs} if needs else set()
        CHECKS.append(fn)
        return fn
    return register


@rule("G1")
def unique_ids(m: Model) -> Iterator[Finding]:
    """Player ids are unique; state ids are unique."""
    for where, ids in (("players", m.player_ids), ("states", m.state_ids)):
        if dups := duplicates(ids):
            yield where, f"duplicate ids: {names(dups)}"


@rule("G2")
def snake_case(m: Model) -> Iterator[Finding]:
    """Every player id, state id and action name is lowercase snake_case."""
    declared = [(f"players[{i}].id", p["id"]) for i, p in enumerate(m.players)]
    declared += [(f"states[{i}].id", s["id"]) for i, s in enumerate(m.states)]
    declared += [(f"{w}.by.{p}", a) for w, e in m.entries for p, a in e["by"].items()]
    for where, name in declared:
        if not ID_RE.match(name):
            yield where, f"{name!r} is not snake_case"


@rule("G3")
def refs_resolve(m: Model) -> Iterator[Finding]:
    """Every state named in `initial` or a `next` is a declared state."""
    for where, dist in m.dists:
        if unknown := sorted({e["state"] for e in dist} - m.declared):
            yield where, f"undeclared state(s): {names(unknown)}"


@rule("G4")
def distributions(m: Model) -> Iterator[Finding]:
    """Probabilities are positive, name each state once, and sum to 1."""
    for where, dist in m.dists:
        if out_of_range := [e["p"] for e in dist if not 0 < e["p"] <= 1]:
            yield where, f"p outside (0, 1]: {names(out_of_range)}"
        if dups := duplicates(e["state"] for e in dist):
            yield where, f"state(s) appearing twice: {names(dups)}"
        total = sum(e["p"] for e in dist)
        if abs(total - 1) > TOL:
            yield where, f"probabilities sum to {total:g}, not 1"


@rule("G5")
def terminal_shape(m: Model) -> Iterator[Finding]:
    """Terminal states carry no `turn` or `actions`; non-terminal states carry both."""
    for where, state in m.items:
        if state["terminal"]:
            if extra := [k for k in ("turn", "actions") if k in state]:
                yield where, f"terminal state carries {names(extra)}"
        elif missing := [k for k in ("turn", "actions") if not state.get(k)]:
            yield where, f"non-terminal state has no {names(missing)}"


@rule("G6")
def turn_names_players(m: Model) -> Iterator[Finding]:
    """`turn` names declared players, without repeats."""
    for where, state in m.items:
        turn = state.get("turn")
        if turn is None:
            continue
        if dups := duplicates(turn):
            yield f"{where}.turn", f"repeated player(s): {names(dups)}"
        if unknown := sorted(set(turn) - set(m.player_ids)):
            yield f"{where}.turn", f"undeclared player(s): {names(unknown)}"


@rule("G7")
def by_matches_turn(m: Model) -> Iterator[Finding]:
    """Every `by` names an action for exactly the players in `turn`."""
    for where, turn, actions in m.moves:
        movers = set(turn)
        for i, entry in enumerate(actions):
            keys = set(entry["by"])
            if keys == movers:
                continue
            bits = [f"{label} {names(sorted(diff))}"
                    for label, diff in (("missing", movers - keys), ("unexpected", keys - movers))
                    if diff]
            yield (f"{where}.actions[{i}].by",
                   f"does not match turn [{names(sorted(movers))}]: {'; '.join(bits)}")


@rule("G8")
def joint_actions_complete(m: Model) -> Iterator[Finding]:
    """The joint actions are exactly the Cartesian product of the movers' choices."""
    for where, turn, actions in m.tables:
        sets, product, missing, repeated = product_diff(turn, actions)
        if not (missing or repeated):
            continue
        shape = f"{' × '.join(sets)} = {' × '.join(str(len(a)) for a in sets.values())}"
        detail = [f"{len(product)} joint actions expected ({shape}), {len(actions)} present"]
        if missing:
            detail.append("missing " + joint(missing))
        if repeated:
            detail.append("repeated " + joint(repeated))
        yield f"{where}.actions", "; ".join(detail)


@rule("G9", needs="G3")
def states_reachable(m: Model) -> Iterator[Finding]:
    """Every declared state is reachable from the support of `initial`."""
    seeds = {e["state"] for e in m.initial}
    if orphans := sorted(m.declared - reachable(seeds, m.edges)):
        yield "states", f"unreachable from initial: {names(orphans)}"


@rule("G10", needs="G3")
def play_can_end(m: Model) -> Iterator[Finding]:
    """A terminal state exists, and every state has a path to one."""
    if not m.terminals:
        yield "states", "no terminal state"
    elif stuck := sorted(m.declared - reachable(m.terminals, m.back_edges)):
        yield "states", f"no path to a terminal state from: {names(stuck)}"


@rule("G11")
def players_act(m: Model) -> Iterator[Finding]:
    """Every declared player appears in at least one state's `turn`."""
    if idle := sorted(set(m.player_ids) - m.acting):
        yield "players", f"never in any turn: {names(idle)}"


# --------------------------------------------------------------------------- the tiers

def parse(raw: str) -> tuple[Any, list[dict]]:
    """Tier 0 — the reply must be exactly one JSON object. Nothing is stripped."""
    try:
        model = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [fail("parse", "reply", f"not valid JSON: {exc}{_hint(raw.strip())}")]
    if not isinstance(model, dict):
        kind = type(model).__name__
        return None, [fail("parse", "reply", f"top level is a {kind}, expected a JSON object")]
    return model, []


def _hint(text: str) -> str:
    """Name the usual way a reply misses tier 0, so the failure reads at a glance."""
    if text.startswith("```"):
        return "; the reply is wrapped in a code fence"
    if "{" in text and not text.startswith("{"):
        return "; the reply has text before the JSON object"
    if text.endswith("```") or (text.endswith((".", "!")) and "}" in text):
        return "; the reply has text after the JSON object"
    return ""


@lru_cache(maxsize=1)
def validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(SCHEMA_PATH.read_text()))


def check_schema(model: Any) -> list[dict]:
    """Tier 1 — structure, types, enums, no invented keys."""
    return [fail("schema", path(e.absolute_path), e.message)
            for e in validator().iter_errors(model)]


def check_rules(m: Model) -> tuple[list[dict], list[str]]:
    """Tier 2 — every registered rule, in order, skipping the undecidable ones."""
    failures, skipped, broken = [], [], set()
    for check in CHECKS:
        if check.needs & broken:
            skipped.append(check.rule)
            continue
        found = [fail(check.rule, where, detail) for where, detail in check(m)]
        if found:
            broken.add(check.rule)
        failures += found
    return failures, skipped


# --------------------------------------------------------------------------- the report

def fail(rule_id: str, where: str, detail: str) -> dict[str, str]:
    return {"rule": rule_id, "where": where, "detail": detail}


def report(failures: list[dict], skipped: list[str], counts: dict | None) -> dict:
    return {"pass": not failures, "failures": failures, "skipped": skipped, "counts": counts}


def check_model(model: Any) -> dict:
    """Tiers 1-2 over an already-parsed model."""
    if schema_failures := check_schema(model):
        return report(schema_failures, [c.rule for c in CHECKS], None)
    m = Model(model)
    failures, skipped = check_rules(m)
    return report(failures, skipped, m.counts)


def check_text(raw: str) -> dict:
    """Tiers 0-2 over a raw reply."""
    model, failures = parse(raw)
    if failures:
        return report(failures, ["schema"] + [c.rule for c in CHECKS], None)
    return check_model(model)


# --------------------------------------------------------------------------- cli

def main(argv: list[str]) -> int:
    if argv:
        path_ = pathlib.Path(argv[0])
        if not path_.is_file():
            print(f"no such file: {path_}", file=sys.stderr)
            return 2
        raw = path_.read_text()
    else:
        raw = sys.stdin.read()

    result = check_text(raw)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
