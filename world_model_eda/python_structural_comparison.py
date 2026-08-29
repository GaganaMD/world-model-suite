"""Renaming-invariant structural comparison for rolled-out Python POSGs.

This module deliberately reuses Souhaila-DJAFFAL's Lane 2 scorer.  Python
objects are never compared directly: each successful exhaustive rollout is
first serialized into the canonical state/action/transition representation and
then adapted to Lane 2's v2 JSON schema.  Rewards and observations remain
available in the canonical rollout but are intentionally outside this
structure-only comparison.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .eda import WorldModelEDA
from .python_posg import canonical_rollout_json


def rollout_to_canonical_document(rollout: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a canonical, label-neutral document for one complete rollout."""
    if rollout.get("errors"):
        raise ValueError("Cannot compare a rollout with validation errors.")
    if rollout.get("truncated"):
        raise ValueError("Cannot compare a truncated rollout.")
    return json.loads(canonical_rollout_json(rollout))


def canonical_to_lane2_model(canonical: Mapping[str, Any]) -> Dict[str, Any]:
    """Adapt canonical rollout JSON to Souhaila's v2 Lane 2 input schema.

    The v2 representation contains players, an initial prior, terminal states,
    joint-action profiles, and successor distributions.  Canonical state IDs
    are used only as opaque identifiers: Lane 2's game matching is invariant
    to player, state, and action renaming.  Observations and rewards are not
    encoded because Lane 2 is explicitly a structural comparison.
    """
    players = [str(player) for player in canonical["players"]]
    state_by_id = {state["id"]: state for state in canonical["states"]}
    transitions_by_state: Dict[str, list[Mapping[str, Any]]] = {}
    for transition in canonical["transitions"]:
        transitions_by_state.setdefault(str(transition["state"]), []).append(transition)

    states = []
    for state_id, state in state_by_id.items():
        terminal = bool(state["terminal"])
        if terminal:
            states.append({"id": state_id, "terminal": True, "turn": [], "actions": []})
            continue

        action_map = state.get("actions", {})
        turn = [player for player in players if player in action_map]
        actions = [
            {
                "by": {
                    player: str(transition["joint_action"][player])
                    for player in turn
                },
                "next": [
                    {
                        "state": str(outcome["next_state"]),
                        "p": float(outcome["probability"]),
                    }
                    for outcome in transition["outcomes"]
                ],
            }
            for transition in transitions_by_state.get(state_id, [])
        ]
        states.append({"id": state_id, "terminal": False, "turn": turn, "actions": actions})

    return {
        "players": [{"id": player} for player in players],
        "initial": [
            {"state": str(item["state"]), "p": float(item["probability"])}
            for item in canonical["initial_distribution"]
        ],
        "states": states,
    }


def rollout_to_lane2_model(rollout: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert a complete Python rollout through canonical JSON to Lane 2."""
    return canonical_to_lane2_model(rollout_to_canonical_document(rollout))


def _lane2_score(
    reference: Mapping[str, Any],
    generated: Mapping[str, Any],
    *,
    horizon: Optional[int],
    sa_iters: int,
    seed: int,
) -> Dict[str, Any]:
    try:
        from json_generation.lane2 import lane2_score
    except ImportError as error:
        raise ImportError(
            "Python structural comparison needs the existing Lane 2 dependencies. "
            "Install or add the external game_matching repository to PYTHONPATH."
        ) from error
    kwargs: Dict[str, Any] = {"sa_iters": sa_iters, "seed": seed}
    if horizon is not None:
        kwargs["horizon"] = horizon
    return lane2_score(reference, generated, **kwargs)


def compare_rollouts(
    reference_rollout: Mapping[str, Any],
    generated_rollout: Mapping[str, Any],
    *,
    horizon: Optional[int] = None,
    sa_iters: int = 3_000,
    seed: int = 0,
) -> Dict[str, Any]:
    """Compare two rolled-out Python POSGs using Lane 2's structural score."""
    reference = rollout_to_lane2_model(reference_rollout)
    generated = rollout_to_lane2_model(generated_rollout)
    score = _lane2_score(
        reference, generated, horizon=horizon, sa_iters=sa_iters, seed=seed
    )
    reference_ids = {state["id"] for state in reference["states"]}
    generated_ids = {state["id"] for state in generated["states"]}
    state_map = score.get("state_map_src", {})
    matched_reference = set(state_map)
    matched_generated = set(state_map.values())
    return {
        **score,
        "structural_status": "PASS" if score["lane2"] > 0.999 else "DIFFERENT",
        "transition_similarity": score["lane2"],
        "unmatched_reference_states": sorted(reference_ids - matched_reference),
        "unmatched_generated_states": sorted(generated_ids - matched_generated),
        "unmatched_actions": [],
        "unmatched_transitions": [],
        "comparison_note": (
            "Lane 2 exposes a renaming-invariant state correspondence. "
            "Action and transition differences are reflected in coverage/precision "
            "but are not returned as itemized correspondences by game_matching."
        ),
    }


def eda_metrics(rollout: Mapping[str, Any]) -> Dict[str, Any]:
    """Return interpretable EDA metrics used in reference/generated rows."""
    summary = WorldModelEDA.from_rollout(rollout).summary()
    return {
        "states": summary["states"]["state_count"],
        "terminal_states": summary["states"]["terminal_state_count"],
        "state_action_pairs": summary["transitions"]["state_action_pair_count"],
        "edges": summary["graph"]["edge_count"],
        "avg_branching": summary["states"]["mean_branching_factor"],
        "stochastic_fraction": summary["transitions"]["stochastic_transition_fraction"],
        "avg_entropy": summary["transitions"]["mean_transition_entropy"],
        "max_depth": summary["states"]["maximum_trajectory_depth"],
        "scc_count": summary["graph"]["strongly_connected_component_count"],
        "avg_terminal_distance": summary["states"]["average_depth_to_terminal"],
    }


def metric_deltas(
    reference_metrics: Mapping[str, Any], generated_metrics: Mapping[str, Any]
) -> Dict[str, Optional[float]]:
    """Return raw deltas and relative errors where the reference value is nonzero."""
    result: Dict[str, Optional[float]] = {}
    for metric, reference_value in reference_metrics.items():
        generated_value = generated_metrics.get(metric)
        if not isinstance(reference_value, (int, float)) or not isinstance(
            generated_value, (int, float)
        ):
            continue
        difference = abs(float(generated_value) - float(reference_value))
        result[f"{metric}_difference"] = difference
        result[f"{metric}_relative_error"] = (
            difference / abs(float(reference_value)) if reference_value != 0 else None
        )
    return result


def comparison_row(
    *,
    case: str,
    model: str,
    sample: int,
    reference_rollout: Mapping[str, Any],
    generated_rollout: Optional[Mapping[str, Any]] = None,
    failure_type: Optional[str] = None,
    **comparison_options: Any,
) -> Dict[str, Any]:
    """Create one export-ready reference-versus-generated result row."""
    reference = eda_metrics(reference_rollout)
    row: Dict[str, Any] = {
        "case": case,
        "model": model,
        "sample": sample,
        "generation_status": "success" if generated_rollout is not None else "failed",
        "execution_status": "success" if generated_rollout is not None else "failed",
        "rollout_status": "success" if generated_rollout is not None else "failed",
        "structural_status": "NOT_EVALUATED",
        "failure_type": failure_type,
        **{f"reference_{key}": value for key, value in reference.items()},
        "reference_actions": reference["state_action_pairs"],
        "reference_entropy": reference["avg_entropy"],
        "reference_depth": reference["max_depth"],
        "reference_scc": reference["scc_count"],
    }
    if generated_rollout is None:
        return row

    generated = eda_metrics(generated_rollout)
    comparison = compare_rollouts(reference_rollout, generated_rollout, **comparison_options)
    row.update(
        {
            **{f"generated_{key}": value for key, value in generated.items()},
            "generated_actions": generated["state_action_pairs"],
            "generated_entropy": generated["avg_entropy"],
            "generated_depth": generated["max_depth"],
            "generated_scc": generated["scc_count"],
            "coverage": comparison["coverage"],
            "precision": comparison["precision"],
            "f1": comparison["lane2"],
            "transition_similarity": comparison["transition_similarity"],
            "structural_status": comparison["structural_status"],
            "failure_type": None,
        }
    )
    row.update(metric_deltas(reference, generated))
    return row


def write_mapping_document(path: str | Path) -> Path:
    """Write a concise, source-controlled mapping of JSON lanes to Python."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        """# JSON evaluation and Python POSG mapping

The JSON and Python tracks are separate generation representations.  The
Python track does not compare Python source code to a JSON reference.  It
first executes and exhaustively rolls out a Python `AbstractPOSG`, exports the
reachable model as canonical state/action/transition JSON, and adapts that
explicit representation to the existing Lane 2 schema.

| Analysis layer | Existing JSON framework | Python POSG track |
| --- | --- | --- |
| Mechanical validity | Lane 1 checks v2 schema, probabilities, action profiles, reachability, and terminal paths. | `validate_posg` and exhaustive rollout check the `AbstractPOSG` interface, finite distributions, hashable states, legal joint actions, observations, rewards, reachability, and rollout bounds. |
| Structural fidelity | Lane 2 uses `game_matching` to compare a candidate and reference up to player/state/action renaming; it returns coverage, precision, and their harmonic mean. | `rollout_to_lane2_model` converts canonical Python rollouts to Lane 2 input, then calls the same scorer. |
| Semantic correctness | Not supplied by mechanical or structural comparison. | Case-specific mechanisms, currently the G1 semantic oracle, inspect intended rewards and observations after structural validation. |
| Exploratory graph EDA | Outside Lane 1/Lane 2. | `WorldModelEDA` measures state/action/transition structure, branching, stochasticity, entropy, depth, SCCs, terminal distance, and degree patterns. |

Lane 2 is intentionally structure-only: canonical rewards and observations are
preserved in Python rollout artifacts but are not passed to `game_matching`.
Consequently, a high structural score is not evidence of semantic correctness.
""",
        encoding="utf-8",
    )
    return destination
