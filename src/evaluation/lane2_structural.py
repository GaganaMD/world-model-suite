"""Lane 2: structural coverage and precision against a reference POSG."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


def _feature_counts(model: Mapping[str, Any]) -> Counter[str]:
    """Name-insensitive structural features used only when game_matching is absent."""
    features: Counter[str] = Counter()
    players = model.get("players", []) or []
    states = model.get("states", []) or []
    features["players"] = len(players)
    features["initial_support"] = len(model.get("initial", []) or [])
    for state in states:
        if not isinstance(state, Mapping):
            continue
        terminal = bool(state.get("terminal", False))
        features["terminal_states" if terminal else "nonterminal_states"] += 1
        turn = state.get("turn", []) or []
        features[f"turn_arity:{len(turn)}"] += 1
        actions = state.get("actions", []) or []
        features[f"profiles_per_state:{len(actions)}"] += 1
        for action in actions:
            if not isinstance(action, Mapping):
                continue
            successors = action.get("next", []) or []
            features[f"transition_support:{len(successors)}"] += 1
            features["transition_edges"] += len(successors)
    return features


def _fallback_score(reference: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    reference_features = _feature_counts(reference)
    candidate_features = _feature_counts(candidate)
    overlap = sum(min(count, candidate_features[key]) for key, count in reference_features.items())
    reference_total = sum(reference_features.values())
    candidate_total = sum(candidate_features.values())
    coverage = overlap / reference_total if reference_total else 0.0
    precision = overlap / candidate_total if candidate_total else 0.0
    combined = 2 * coverage * precision / (coverage + precision) if coverage + precision else 0.0
    return {
        "coverage": round(coverage, 4),
        "precision": round(precision, 4),
        "combined_score": round(combined, 4),
        "details": {
            "backend": "feature_multiset_fallback",
            "warning": "game_matching is unavailable; scores are name-insensitive feature overlap, not optimal graph matching.",
            "reference_features": dict(reference_features),
            "candidate_features": dict(candidate_features),
        },
    }


def evaluate_structural(
    candidate: Mapping[str, Any],
    ground_truth: Mapping[str, Any] | None,
    *,
    horizon: int = 3,
    unroll: str = "always",
    sa_iters: int = 3000,
    seed: int = 0,
) -> dict[str, Any]:
    if ground_truth is None:
        return {
            "coverage": 0.0,
            "precision": 0.0,
            "combined_score": 0.0,
            "details": {"skipped": True, "reason": "ground_truth_path was not provided"},
        }
    try:
        from json_generation.lane2 import lane2_score

        score = lane2_score(
            ground_truth,
            candidate,
            horizon=horizon,
            unroll=unroll,
            sa_iters=sa_iters,
            seed=seed,
        )
        return {
            "coverage": float(score["coverage"]),
            "precision": float(score["precision"]),
            "combined_score": float(score["lane2"]),
            "details": {
                "backend": "game_matching",
                "player_map": score.get("player_map", {}),
                "state_map": score.get("state_map_src", {}),
                "assumptions": score.get("assumptions", []),
            },
        }
    except ImportError as error:
        result = _fallback_score(ground_truth, candidate)
        result["details"]["dependency_error"] = str(error)
        return result

