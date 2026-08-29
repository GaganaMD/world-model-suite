"""Lane 3: deterministic coverage, plausibility, and bias-risk checklist."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Mapping


SENSITIVE_TERMS = re.compile(
    r"\b(gender|male|female|man|woman|race|racial|religion|religious|caste|ethnicity|ethnic|"
    r"disability|disabled|senior|junior|nationality)\b",
    re.IGNORECASE,
)


def evaluate_qualitative(
    model: Mapping[str, Any],
    ground_truth: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    players = model.get("players", []) or []
    states = model.get("states", []) or []
    checklist: dict[str, bool] = {}
    checklist["stakeholders_present"] = bool(players)
    checklist["stakeholders_described"] = all(
        isinstance(player, Mapping) and bool(player.get("desc") or player.get("description"))
        for player in players
    )
    nonterminal = [state for state in states if isinstance(state, Mapping) and not state.get("terminal", False)]
    checklist["nonterminal_actions_present"] = bool(nonterminal) and all(state.get("actions") for state in nonterminal)
    checklist["states_described"] = all(
        isinstance(state, Mapping) and bool(state.get("desc") or state.get("description")) for state in states
    )
    checklist["consequences_represented"] = any(
        successor
        for state in nonterminal
        for action in state.get("actions", []) or []
        if isinstance(action, Mapping)
        for successor in action.get("next", []) or []
    )

    action_counts: Counter[str] = Counter()
    for state in nonterminal:
        for action in state.get("actions", []) or []:
            if not isinstance(action, Mapping):
                continue
            for player in action.get("by", {}) or {}:
                action_counts[str(player)] += 1
    counts = list(action_counts.values())
    disparity = (max(counts) - min(counts)) if len(counts) > 1 else 0
    text = " ".join(
        str(value)
        for collection in (players, states)
        for item in collection
        if isinstance(item, Mapping)
        for value in item.values()
        if isinstance(value, str)
    )
    sensitive_mentions = sorted(set(match.group(0).lower() for match in SENSITIVE_TERMS.finditer(text)))
    bias_flags = []
    if disparity:
        bias_flags.append(f"action-profile representation differs across players by {disparity}")
    if sensitive_mentions:
        bias_flags.append("sensitive/proxy terms require human or counterfactual review: " + ", ".join(sensitive_mentions))

    reference_players = {
        str(player.get("id")) for player in (ground_truth or {}).get("players", []) if isinstance(player, Mapping)
    }
    candidate_players = {str(player.get("id")) for player in players if isinstance(player, Mapping)}
    stakeholder_coverage = (
        len(reference_players & candidate_players) / len(reference_players) if reference_players else None
    )
    passed = all(checklist.values())
    return {
        "checklist_passed": passed,
        "details": {
            "checklist": checklist,
            "bias_flags": bias_flags,
            "bias_check_passed": not bias_flags,
            "action_profile_counts_by_player": dict(action_counts),
            "maximum_action_count_disparity": disparity,
            "stakeholder_coverage": stakeholder_coverage,
            "human_review_required": bool(bias_flags),
            "note": "Flags are diagnostic only; statistical/counterfactual evidence is required before calling a disparity bias.",
        },
    }

