"""Small explicit semantic oracle for the G1 Rock-Paper-Scissors case."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Any, Dict, Mapping

from .python_posg import AbstractPOSG, execute_generated_posg, rollout_world_model


PLAYERS = ("player_1", "player_2")
ACTIONS = ("rock", "paper", "scissors")
PLAYER_1_WINS = {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}


def _expected_outcome(first: str, second: str) -> str:
    if first == second:
        return "draw"
    return "player_1_wins" if (first, second) in PLAYER_1_WINS else "player_2_wins"


def _check(status: str, detail: str) -> Dict[str, str]:
    return {"status": status, "detail": detail}


def evaluate_g1_rollout(rollout: Mapping[str, Any]) -> Dict[str, Any]:
    """Evaluate G1 semantics from an existing structural rollout.

    The result is deliberately an explicit test-case oracle, not a generic
    natural-language evaluator. ``UNKNOWN`` is reserved for observations that
    do not contain enough outcome language to establish a contradiction.
    """
    if rollout["errors"] or rollout["truncated"]:
        reason = "; ".join(rollout["errors"] or rollout["warnings"])
        return {
            "case": "G1",
            "structural_validity": "FAIL",
            "semantic_validity": "NOT_EVALUATED",
            "semantic_score": None,
            "checks": {},
            "failures": [reason],
        }

    checks: Dict[str, Dict[str, str]] = {}
    failures: list[str] = []
    initial_states = list(rollout["initial_distribution"])
    transitions = [
        record for record in rollout["transitions"] if record["state"] in initial_states
    ]

    players_ok = tuple(rollout["players"]) == PLAYERS
    checks["players"] = _check(
        "PASS" if players_ok else "FAIL",
        f"Expected {PLAYERS}; found {tuple(rollout['players'])}.",
    )

    initial_action_maps = [rollout["actions"].get(state, {}) for state in initial_states]
    actions_ok = (
        len(initial_action_maps) == 1
        and all(set(initial_action_maps[0].get(player, [])) == set(ACTIONS) for player in PLAYERS)
    )
    checks["actions"] = _check(
        "PASS" if actions_ok else "FAIL",
        "Both initial players expose exactly rock, paper, and scissors."
        if actions_ok
        else "Initial action sets do not match RPS.",
    )

    profiles = {
        tuple(record["joint_action"].get(player) for player in PLAYERS): record
        for record in transitions
    }
    expected_profiles = set(product(ACTIONS, repeat=2))
    coverage_ok = set(profiles) == expected_profiles
    checks["joint_actions"] = _check(
        "PASS" if coverage_ok else "FAIL",
        f"Expected 9 RPS profiles; found {len(profiles)}.",
    )
    simultaneous_ok = coverage_ok and len(transitions) == 9
    checks["simultaneous_play"] = _check(
        "PASS" if simultaneous_ok else "FAIL",
        "Both players act in one shared initial state."
        if simultaneous_ok
        else "The initial decision structure is not the nine simultaneous profiles.",
    )

    outcomes: Dict[tuple[str, str], Any] = {}
    valid_distributions = True
    for profile, record in profiles.items():
        if len(record["outcomes"]) != 1 or record["outcomes"][0]["probability"] != 1.0:
            valid_distributions = False
            continue
        outcomes[profile] = record["outcomes"][0]

    grouped_states: Dict[str, set[Any]] = {"player_1_wins": set(), "player_2_wins": set(), "draw": set()}
    for profile, outcome in outcomes.items():
        grouped_states[_expected_outcome(*profile)].add(outcome["next_state"])
    transition_ok = (
        coverage_ok
        and valid_distributions
        and all(len(states) == 1 for states in grouped_states.values())
        and len(set().union(*grouped_states.values())) == 3
        and all(
            rollout["states"][next(iter(states))]["terminal"]
            for states in grouped_states.values()
            if states
        )
    )
    checks["transitions"] = _check(
        "PASS" if transition_ok else "FAIL",
        "All nine profiles deterministically partition into three distinct terminal outcome states."
        if transition_ok
        else "RPS outcome partition or deterministic terminal transition requirement failed.",
    )

    reward_ok = coverage_ok and valid_distributions
    if reward_ok:
        for profile, outcome in outcomes.items():
            expected = _expected_outcome(*profile)
            expected_rewards = (
                {"player_1": 0.0, "player_2": 0.0}
                if expected == "draw"
                else {"player_1": 1.0, "player_2": -1.0}
                if expected == "player_1_wins"
                else {"player_1": -1.0, "player_2": 1.0}
            )
            if outcome["rewards"] != expected_rewards:
                reward_ok = False
                break
    checks["rewards"] = _check(
        "PASS" if reward_ok else "FAIL",
        "Every profile has the expected zero-sum reward pair."
        if reward_ok
        else "At least one profile has incorrect RPS rewards.",
    )

    terminal_ok = len(rollout["terminal_states"]) == 3
    checks["terminal_states"] = _check(
        "PASS" if terminal_ok else "FAIL",
        f"Expected 3 terminal states; found {len(rollout['terminal_states'])}.",
    )
    checks["observations"] = _observation_check(outcomes)

    for name, check in checks.items():
        if check["status"] == "FAIL":
            failures.append(f"{name}: {check['detail']}")
    applicable = [check for check in checks.values() if check["status"] != "UNKNOWN"]
    passed = sum(check["status"] == "PASS" for check in applicable)
    semantic_status = "FAIL" if failures else "PASS" if applicable else "UNKNOWN"
    return {
        "case": "G1",
        "structural_validity": "PASS",
        "semantic_validity": semantic_status,
        "semantic_score": passed / len(applicable) if applicable else None,
        "checks": checks,
        "failures": failures,
    }


def _observation_check(outcomes: Mapping[tuple[str, str], Mapping[str, Any]]) -> Dict[str, str]:
    """Flag explicit winner/loser contradictions; neutral observations remain unknown."""
    saw_interpretable_observation = False
    for profile, outcome in outcomes.items():
        expected = _expected_outcome(*profile)
        for player, observation in outcome["observations"].items():
            normalized = observation.lower().replace("_", " ")
            if not any(word in normalized for word in ("win", "lose", "draw")):
                continue
            saw_interpretable_observation = True
            if expected == "draw" and ("win" in normalized or "lose" in normalized):
                return _check("FAIL", f"{player} reports a win/loss for draw profile {profile}.")
            winner = "player 1" if expected == "player_1_wins" else "player 2"
            loser = "player 2" if expected == "player_1_wins" else "player 1"
            if expected != "draw" and (
                f"{loser} wins" in normalized or f"{winner} loses" in normalized
            ):
                return _check("FAIL", f"{player} observation contradicts outcome for profile {profile}.")
    return _check(
        "PASS" if saw_interpretable_observation else "UNKNOWN",
        "No explicit observation contradiction found."
        if saw_interpretable_observation
        else "Observations contain no outcome language to check.",
    )


def evaluate_g1_posg(posg: AbstractPOSG) -> Dict[str, Any]:
    """Roll out and evaluate one already-instantiated generated Python POSG."""
    return evaluate_g1_rollout(rollout_world_model(posg))


def evaluate_g1_source(source: str) -> Dict[str, Any]:
    """Execute and evaluate generated source while preserving structural failure separation."""
    execution = execute_generated_posg(source)
    if not execution["success"]:
        return {
            "case": "G1",
            "structural_validity": "FAIL",
            "semantic_validity": "NOT_EVALUATED",
            "semantic_score": None,
            "checks": {},
            "failures": execution["errors"],
        }
    return evaluate_g1_posg(execution["world_model"])


def evaluate_g1_artifact(path: str | Path) -> Dict[str, Any]:
    """Evaluate a saved ``generated.py`` experiment artifact."""
    return evaluate_g1_source(Path(path).read_text(encoding="utf-8"))
