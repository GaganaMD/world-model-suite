"""Lane 1: schema and mechanical validity checks for v2 POSG documents."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from itertools import product
from math import isfinite
from typing import Any, Mapping

import networkx as nx


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str
    category: str
    message: str


def _finding(check: str, message: str, category: str = "mechanical", severity: str = "error") -> Finding:
    return Finding(check, severity, category, message)


def build_transition_graph(model: Mapping[str, Any]) -> nx.DiGraph:
    """Build a graph whose node identifiers are always strings."""
    graph = nx.DiGraph()
    for state in model.get("states", []) if isinstance(model.get("states"), list) else []:
        if not isinstance(state, Mapping) or "id" not in state:
            continue
        source = str(state["id"])
        graph.add_node(source, terminal=bool(state.get("terminal", False)))
        for action in state.get("actions", []) or []:
            if not isinstance(action, Mapping):
                continue
            for successor in action.get("next", []) or []:
                if isinstance(successor, Mapping) and "state" in successor:
                    graph.add_edge(source, str(successor["state"]))
    return graph


def evaluate_mechanical(model: Mapping[str, Any], probability_tolerance: float = 1e-3) -> dict[str, Any]:
    """Run ev1/ev2 schema, probability, action-profile, and reachability checks."""
    findings: list[Finding] = []
    if not isinstance(model, Mapping):
        findings.append(_finding("SCHEMA-model", "model must be a JSON object", "schema"))
        return _result(findings, {}, set(), set())

    for key in ("players", "initial", "states"):
        if key not in model:
            findings.append(_finding("SCHEMA-keys", f"missing top-level '{key}'", "schema"))
    if findings:
        return _result(findings, {}, set(), set())

    players = model["players"]
    initial = model["initial"]
    states = model["states"]
    if not isinstance(players, list) or not players:
        findings.append(_finding("SCHEMA-players", "'players' must be a non-empty list", "schema"))
    if not isinstance(initial, list) or not initial:
        findings.append(_finding("SCHEMA-initial", "'initial' must be a non-empty prior list", "schema"))
    if not isinstance(states, list) or not states:
        findings.append(_finding("SCHEMA-states", "'states' must be a non-empty list", "schema"))
    if findings:
        return _result(findings, {}, set(), set())

    player_ids = []
    for index, player in enumerate(players):
        if not isinstance(player, Mapping) or "id" not in player:
            findings.append(_finding("SCHEMA-player", f"player {index} must contain an id", "schema"))
        else:
            player_ids.append(str(player["id"]))
    if len(player_ids) != len(set(player_ids)):
        findings.append(_finding("G1-dup-player", f"duplicate player ids: {player_ids}", "schema"))

    state_map: dict[str, Mapping[str, Any]] = {}
    for index, state in enumerate(states):
        if not isinstance(state, Mapping) or "id" not in state:
            findings.append(_finding("SCHEMA-state", f"state {index} must contain an id", "schema"))
            continue
        state_id = str(state["id"])
        if state_id in state_map:
            findings.append(_finding("G1-dup-state", f"duplicate state id '{state_id}'", "schema"))
        state_map[state_id] = state

    initial_total = 0.0
    initial_ids: list[str] = []
    for index, entry in enumerate(initial):
        if not isinstance(entry, Mapping) or "state" not in entry or "p" not in entry:
            findings.append(_finding("SCHEMA-initial-entry", f"initial entry {index} needs state and p", "schema"))
            continue
        state_id = str(entry["state"])
        initial_ids.append(state_id)
        probability = entry["p"]
        if state_id not in state_map:
            findings.append(_finding("MECH-initial", f"initial references undeclared state '{state_id}'"))
        if not isinstance(probability, (int, float)) or not isfinite(float(probability)) or probability <= 0:
            findings.append(_finding("G4-initial-pos", f"invalid initial probability {probability!r} for '{state_id}'"))
        else:
            initial_total += float(probability)
    if abs(initial_total - 1.0) > probability_tolerance:
        findings.append(_finding("G4-initial-sum", f"initial prior sums to {initial_total}, not 1"))

    acting_players: set[str] = set()
    for state_id, state in state_map.items():
        terminal = bool(state.get("terminal", False))
        turn_raw = state.get("turn", []) or []
        actions = state.get("actions", []) or []
        turn = [str(value) for value in turn_raw] if isinstance(turn_raw, list) else []
        if not isinstance(turn_raw, list):
            findings.append(_finding("SCHEMA-turn", f"state '{state_id}': turn must be a list", "schema"))
        if not isinstance(actions, list):
            findings.append(_finding("SCHEMA-actions", f"state '{state_id}': actions must be a list", "schema"))
            actions = []
        if terminal:
            if turn or actions:
                findings.append(_finding("G5-terminal", f"terminal state '{state_id}' has turn/actions"))
            continue
        if not turn:
            findings.append(_finding("G5-nonterminal", f"non-terminal '{state_id}' has no turn"))
        if not actions:
            findings.append(_finding("G5-nonterminal", f"non-terminal '{state_id}' has no actions"))
        acting_players.update(turn)
        for player in turn:
            if player not in player_ids:
                findings.append(_finding("G6-turn", f"state '{state_id}' names undeclared player '{player}'"))

        profiles: set[tuple[tuple[str, str], ...]] = set()
        per_player: dict[str, set[str]] = {player: set() for player in turn}
        for action_index, action in enumerate(actions):
            if not isinstance(action, Mapping):
                findings.append(_finding("SCHEMA-action", f"state '{state_id}' action {action_index} is not an object", "schema"))
                continue
            by = action.get("by", {})
            if not isinstance(by, Mapping):
                findings.append(_finding("G7-profile", f"state '{state_id}': action by must be an object"))
                by = {}
            by_normalized = {str(key): value for key, value in by.items()}
            if set(by_normalized) != set(turn):
                findings.append(_finding("G7-profile", f"state '{state_id}': action players {set(by_normalized)} != turn {set(turn)}"))
            bad_actions = [value for value in by_normalized.values() if not isinstance(value, str)]
            if bad_actions:
                findings.append(_finding("G7-action-type", f"state '{state_id}': action identifiers must be strings, got {bad_actions!r}"))
            key = tuple(sorted((player, str(value)) for player, value in by_normalized.items()))
            if key in profiles:
                findings.append(_finding("G8-dup-profile", f"state '{state_id}': duplicate action profile {dict(key)}"))
            profiles.add(key)
            for player in turn:
                if player in by_normalized:
                    per_player[player].add(str(by_normalized[player]))

            successors = action.get("next", [])
            if not isinstance(successors, list) or not successors:
                findings.append(_finding("G4-next", f"state '{state_id}' profile {dict(key)} has no successors"))
                continue
            total = 0.0
            for successor in successors:
                if not isinstance(successor, Mapping) or "state" not in successor or "p" not in successor:
                    findings.append(_finding("SCHEMA-next", f"state '{state_id}' has malformed successor", "schema"))
                    continue
                target = str(successor["state"])
                probability = successor["p"]
                if target not in state_map:
                    findings.append(_finding("MECH-next", f"state '{state_id}' transitions to undeclared '{target}'"))
                if not isinstance(probability, (int, float)) or not isfinite(float(probability)) or probability <= 0:
                    findings.append(_finding("G4-pos", f"state '{state_id}' has invalid probability {probability!r}"))
                else:
                    total += float(probability)
            if abs(total - 1.0) > probability_tolerance:
                findings.append(_finding("G4-sum", f"state '{state_id}' profile {dict(key)} sums to {total}, not 1"))

        if turn and all(per_player[player] for player in turn):
            expected = {
                tuple(sorted(zip(turn, values)))
                for values in product(*(sorted(per_player[player]) for player in turn))
            }
            for missing in sorted(expected - profiles):
                findings.append(_finding("G7-incomplete", f"state '{state_id}': missing action profile {dict(missing)}"))

    for player in player_ids:
        if player not in acting_players:
            findings.append(_finding("G11-idle-player", f"player '{player}' never acts", severity="warning"))

    graph = build_transition_graph(model)
    reachable: set[str] = set()
    queue = deque(initial_ids)
    while queue:
        state_id = queue.popleft()
        if state_id in reachable or state_id not in graph:
            continue
        reachable.add(state_id)
        queue.extend(str(target) for target in graph.successors(state_id))
    for state_id in state_map:
        if state_id not in reachable:
            findings.append(_finding("G9-unreachable", f"state '{state_id}' is unreachable from initial"))

    terminals = {state_id for state_id, state in state_map.items() if state.get("terminal", False)}
    if not terminals:
        findings.append(_finding("G10-no-terminal", "no terminal state exists"))
        terminal_reachable: set[str] = set()
    else:
        reverse = graph.reverse(copy=False)
        terminal_reachable = set(terminals)
        queue = deque(terminals)
        while queue:
            state_id = queue.popleft()
            for predecessor in reverse.neighbors(state_id):
                predecessor_id = str(predecessor)
                if predecessor_id not in terminal_reachable:
                    terminal_reachable.add(predecessor_id)
                    queue.append(predecessor_id)
        for state_id in state_map:
            if state_id not in terminal_reachable:
                findings.append(_finding("G10-no-path-to-terminal", f"state '{state_id}' has no path to a terminal"))

    return _result(findings, state_map, reachable, terminal_reachable)


def _result(findings: list[Finding], states: Mapping[str, Any], reachable: set[str], terminal_reachable: set[str]) -> dict[str, Any]:
    errors = [finding.message for finding in findings if finding.severity == "error"]
    warnings = [finding.message for finding in findings if finding.severity == "warning"]
    return {
        "passed": not errors,
        "errors": errors,
        "details": {
            "findings": [asdict(finding) for finding in findings],
            "warnings": warnings,
            "state_count": len(states),
            "reachable_states": sorted(reachable),
            "states_with_terminal_path": sorted(terminal_reachable),
        },
    }
