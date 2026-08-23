"""Rollout, validation, and graph utilities for generated Python POSGs."""

from __future__ import annotations

import abc
import ast
import itertools
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Hashable, Iterable, List, Mapping, Optional

import networkx as nx


class AbstractPOSG(abc.ABC):
    """Canonical interface implemented by generated Python world models."""

    @property
    @abc.abstractmethod
    def players(self) -> List[str]:
        """Return player IDs."""

    @abc.abstractmethod
    def legal_actions(self, state: Hashable, player: str) -> List[str]:
        """Return legal actions for ``player`` in ``state``."""

    @abc.abstractmethod
    def transition(
        self, state: Hashable, joint_action: Dict[str, str]
    ) -> Dict[Hashable, float]:
        """Return ``P(next_state | state, joint_action)`` without sampling."""

    @abc.abstractmethod
    def observation(
        self, state: Hashable, joint_action: Dict[str, str], next_state: Hashable, player: str
    ) -> str:
        """Return the observation received by ``player`` after a transition."""

    @abc.abstractmethod
    def reward(
        self, state: Hashable, joint_action: Dict[str, str], next_state: Hashable, player: str
    ) -> float:
        """Return the immediate reward for ``player``."""

    @abc.abstractmethod
    def is_terminal(self, state: Hashable) -> bool:
        """Return whether ``state`` is terminal."""

    @abc.abstractmethod
    def initial_state(self) -> Any:
        """Return an initial state or a distribution mapping states to probabilities."""


def _initial_distribution(initial: Any) -> Dict[Hashable, float]:
    """Normalize either supported form of ``initial_state``."""
    if isinstance(initial, Mapping) and initial and all(
        isinstance(probability, (int, float)) for probability in initial.values()
    ):
        distribution = {state: float(probability) for state, probability in initial.items()}
    else:
        distribution = {initial: 1.0}
    _validate_distribution(distribution, "initial_state()")
    return distribution


def _validate_distribution(distribution: Any, context: str) -> None:
    if not isinstance(distribution, Mapping) or not distribution:
        raise ValueError(f"{context} must return a non-empty dictionary of state probabilities.")
    total = 0.0
    for state, probability in distribution.items():
        try:
            hash(state)
        except TypeError as error:
            raise ValueError(f"{context} returned an unhashable state {state!r}.") from error
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise ValueError(f"{context} has a non-numeric probability for {state!r}.")
        if not math.isfinite(probability) or probability < 0.0 or probability > 1.0:
            raise ValueError(f"{context} has invalid probability {probability!r} for {state!r}.")
        total += probability
    if not math.isclose(total, 1.0, abs_tol=1e-8):
        raise ValueError(f"{context} probabilities sum to {total}, not 1.0.")


def _state_key(state: Hashable) -> str:
    return repr(state)


def summarize_rollout(rollout: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a compact, inspection-friendly structural world-model summary."""
    state_actions = len(rollout["transitions"])
    stochastic = sum(len(record["outcomes"]) > 1 for record in rollout["transitions"])
    return {
        "players": list(rollout["players"]),
        "initial_state_count": len(rollout["initial_distribution"]),
        "reachable_state_count": len(rollout["states"]),
        "terminal_state_count": len(rollout["terminal_states"]),
        "non_terminal_state_count": len(rollout["states"]) - len(rollout["terminal_states"]),
        "joint_action_count": state_actions,
        "transition_outcome_count": sum(len(record["outcomes"]) for record in rollout["transitions"]),
        "stochastic_state_action_count": stochastic,
        "truncated": rollout["truncated"],
        "errors": list(rollout["errors"]),
        "warnings": list(rollout["warnings"]),
    }


def canonical_rollout_json(rollout: Mapping[str, Any], *, indent: int = 2) -> str:
    """Serialize a rolled-out Python world model deterministically as canonical JSON."""
    ordered_states = sorted(rollout["states"], key=_state_key)
    state_ids = {state: f"state_{index:04d}" for index, state in enumerate(ordered_states)}

    def action_key(actions: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(actions.items()))

    document = {
        "players": list(rollout["players"]),
        "initial_distribution": [
            {"state": state_ids[state], "probability": probability}
            for state, probability in sorted(
                rollout["initial_distribution"].items(), key=lambda item: state_ids[item[0]]
            )
        ],
        "states": [
            {
                "id": state_ids[state],
                "representation": _state_key(state),
                "terminal": rollout["states"][state]["terminal"],
                "depth": rollout["states"][state]["depth"],
                "actions": rollout["actions"].get(state, {}),
            }
            for state in ordered_states
        ],
        "transitions": [
            {
                "state": state_ids[record["state"]],
                "joint_action": record["joint_action"],
                "outcomes": [
                    {
                        "next_state": state_ids[outcome["next_state"]],
                        "probability": outcome["probability"],
                        "observations": outcome["observations"],
                        "rewards": outcome["rewards"],
                    }
                    for outcome in sorted(
                        record["outcomes"], key=lambda outcome: state_ids[outcome["next_state"]]
                    )
                ],
            }
            for record in sorted(
                rollout["transitions"],
                key=lambda record: (state_ids[record["state"]], action_key(record["joint_action"])),
            )
        ],
        "truncated": rollout["truncated"],
        "warnings": sorted(rollout["warnings"]),
        "errors": sorted(rollout["errors"]),
    }
    return json.dumps(document, indent=indent, sort_keys=True, ensure_ascii=True) + "\n"


def export_rollout_json(rollout: Mapping[str, Any], path: str | Path) -> Path:
    """Write :func:`canonical_rollout_json` to ``path``."""
    destination = Path(path)
    destination.write_text(canonical_rollout_json(rollout), encoding="utf-8")
    return destination


def classify_failure(result: Mapping[str, Any]) -> Dict[str, str]:
    """Classify an experiment failure for cross-model failure analysis."""
    message = "\n".join(result.get("errors", []))
    categories = (
        ("invalid_python", ("SyntaxError",)),
        ("interface_failure", ("AbstractPOSG", "GeneratedPOSG", "redefine")),
        ("invalid_actions", ("legal_actions", "action")),
        ("invalid_probability", ("probability", "sum to")),
        ("unhashable_state", ("unhashable",)),
        ("observation_failure", ("observation",)),
        ("reward_failure", ("reward",)),
        ("invalid_terminal_structure", ("terminal",)),
        ("rollout_limit", ("max_states", "max_depth")),
        ("invalid_transition", ("Transition", "transition")),
    )
    category = next(
        (name for name, indicators in categories if any(indicator in message for indicator in indicators)),
        "other",
    )
    return {"failure_type": category, "error_message": message}


def batch_posg_cases(
    cases: Mapping[str, AbstractPOSG],
    *,
    model_name: str = "reference",
    max_states: int = 1_000,
    max_depth: int = 20,
) -> List[Dict[str, Any]]:
    """Roll out a named collection of Python POSGs into cross-case EDA rows."""
    from .eda import WorldModelEDA

    rows = []
    for case, posg in cases.items():
        validation = validate_posg(posg, max_states=max_states, max_depth=max_depth)
        row: Dict[str, Any] = {"case": case, "model": model_name, "status": "success"}
        if not validation["passed"]:
            row.update({"status": "failure", **classify_failure(validation)})
            rows.append(row)
            continue
        eda = WorldModelEDA.from_rollout(validation["rollout"])
        summary = eda.summary()
        centrality = eda.centrality_analysis()
        degrees = [degree for _, degree in eda.build_state_graph().degree()]
        row.update(
            {
                "states": summary["states"]["state_count"],
                "terminal_states": summary["states"]["terminal_state_count"],
                "edges": summary["graph"]["edge_count"],
                "avg_branching": summary["states"]["mean_branching_factor"],
                "max_branching": summary["states"]["maximum_branching_factor"],
                "deterministic_fraction": summary["transitions"]["deterministic_transition_fraction"],
                "stochastic_fraction": summary["transitions"]["stochastic_transition_fraction"],
                "avg_entropy": summary["transitions"]["mean_transition_entropy"],
                "max_entropy": summary["transitions"]["maximum_transition_entropy"],
                "density": summary["graph"]["density"],
                "scc_count": summary["graph"]["strongly_connected_component_count"],
                "largest_scc": summary["graph"]["largest_strongly_connected_component_size"],
                "max_depth": summary["states"]["maximum_trajectory_depth"],
                "avg_terminal_distance": summary["states"]["average_depth_to_terminal"],
                "avg_degree": sum(degrees) / len(degrees) if degrees else None,
                "max_degree": max(degrees, default=None),
                "avg_betweenness": (
                    sum(centrality["betweenness"].values()) / len(centrality["betweenness"])
                    if centrality["betweenness"]
                    else None
                ),
                "warnings": validation["warnings"],
                "rollout": validation["rollout"],
                "eda_summary": summary,
            }
        )
        rows.append(row)
    return rows


def plot_cross_case_eda(rows: Iterable[Mapping[str, Any]]) -> Any:
    """Plot six compact cross-case structural descriptors for successful runs."""
    import matplotlib.pyplot as plt

    successful = [row for row in rows if row["status"] == "success"]
    cases = [row["case"] for row in successful]
    metrics = [
        ("states", "Reachable states"),
        ("edges", "State-graph edges"),
        ("avg_branching", "Average joint-action branching"),
        ("avg_entropy", "Mean transition entropy (bits)"),
        ("max_depth", "Maximum trajectory depth"),
        ("scc_count", "Strongly connected components"),
    ]
    figure, axes = plt.subplots(2, 3, figsize=(14, 7), constrained_layout=True)
    for axis, (key, title) in zip(axes.flat, metrics):
        values = [row[key] if row[key] is not None else float("nan") for row in successful]
        axis.bar(cases, values, color="#457b9d")
        axis.set_title(title)
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    return figure


def rollout_world_model(
    posg: AbstractPOSG,
    *,
    max_states: int = 1_000,
    max_depth: int = 20,
) -> Dict[str, Any]:
    """Exhaustively enumerate the finite reachable portion of a generated POSG.

    Invalid transitions are recorded under ``errors`` and do not abort unrelated branches.
    ``truncated`` and ``warnings`` make state/depth limits explicit rather than silent.
    """
    result: Dict[str, Any] = {
        "players": [],
        "initial_distribution": {},
        "states": {},
        "actions": {},
        "transitions": [],
        "terminal_states": [],
        "warnings": [],
        "errors": [],
        "truncated": False,
        "max_states": max_states,
        "max_depth": max_depth,
    }
    try:
        players = list(posg.players)
        if not players or len(set(players)) != len(players) or not all(isinstance(player, str) for player in players):
            raise ValueError("players must be a non-empty list of unique string IDs.")
        initial_distribution = _initial_distribution(posg.initial_state())
    except Exception as error:
        result["errors"].append(f"POSG setup failed: {type(error).__name__}: {error}")
        return result

    result["players"] = players
    result["initial_distribution"] = initial_distribution
    queue = deque((state, 0) for state in initial_distribution)
    seen: set[Hashable] = set()

    while queue:
        state, depth = queue.popleft()
        if state in seen:
            continue
        if len(seen) >= max_states:
            result["truncated"] = True
            result["warnings"].append(f"Exploration stopped at max_states={max_states}.")
            break
        seen.add(state)
        state_data = {"terminal": False, "depth": depth}
        result["states"][state] = state_data

        try:
            terminal = posg.is_terminal(state)
            if not isinstance(terminal, bool):
                raise TypeError("is_terminal() must return bool.")
        except Exception as error:
            result["errors"].append(f"State {_state_key(state)}: is_terminal failed: {error}")
            continue
        state_data["terminal"] = terminal
        if terminal:
            result["terminal_states"].append(state)
            if state in initial_distribution:
                result["errors"].append(
                    f"Initial state {_state_key(state)} is terminal; an interactive POSG needs a decision state."
                )
            continue
        if depth >= max_depth:
            result["truncated"] = True
            result["warnings"].append(
                f"State {_state_key(state)} at depth {depth} was not expanded (max_depth={max_depth})."
            )
            continue

        legal_actions: Dict[str, List[str]] = {}
        malformed = False
        for player in players:
            try:
                actions = posg.legal_actions(state, player)
                if not isinstance(actions, list) or not actions or not all(isinstance(action, str) for action in actions):
                    raise ValueError("must return a non-empty list of string actions.")
                if len(set(actions)) != len(actions):
                    raise ValueError("must not return duplicate actions.")
                legal_actions[player] = actions
            except Exception as error:
                result["errors"].append(
                    f"State {_state_key(state)}, player {player!r}: legal_actions {error}"
                )
                malformed = True
        if malformed:
            continue
        result["actions"][state] = legal_actions

        for action_values in itertools.product(*(legal_actions[player] for player in players)):
            joint_action = dict(zip(players, action_values))
            try:
                distribution = posg.transition(state, joint_action)
                _validate_distribution(
                    distribution, f"transition({_state_key(state)}, {joint_action!r})"
                )
            except Exception as error:
                result["errors"].append(f"Transition failed: {type(error).__name__}: {error}")
                continue

            transition_record = {
                "state": state,
                "joint_action": joint_action,
                "outcomes": [],
            }
            for next_state, probability in distribution.items():
                outcome = {"next_state": next_state, "probability": float(probability), "observations": {}, "rewards": {}}
                for player in players:
                    try:
                        observation = posg.observation(state, joint_action, next_state, player)
                        reward = posg.reward(state, joint_action, next_state, player)
                        if not isinstance(observation, str):
                            raise TypeError("observation() must return str.")
                        if isinstance(reward, bool) or not isinstance(reward, (int, float)) or not math.isfinite(reward):
                            raise TypeError("reward() must return a finite number.")
                        outcome["observations"][player] = observation
                        outcome["rewards"][player] = float(reward)
                    except Exception as error:
                        result["errors"].append(
                            f"Outcome {_state_key(next_state)}, player {player!r}: {type(error).__name__}: {error}"
                        )
                transition_record["outcomes"].append(outcome)
                if next_state not in seen:
                    queue.append((next_state, depth + 1))
            result["transitions"].append(transition_record)

    return result


def validate_posg(
    posg_or_class: Any, *, max_states: int = 1_000, max_depth: int = 20
) -> Dict[str, Any]:
    """Return structured, exhaustive validation results for small generated POSGs."""
    try:
        posg = posg_or_class() if isinstance(posg_or_class, type) else posg_or_class
        if not isinstance(posg, AbstractPOSG):
            raise TypeError("GeneratedPOSG must inherit from AbstractPOSG.")
    except Exception as error:
        return {
            "passed": False,
            "errors": [f"Instantiation failed: {type(error).__name__}: {error}"],
            "warnings": [],
            "states_checked": 0,
            "transitions_checked": 0,
            "rollout": None,
        }
    rollout = rollout_world_model(posg, max_states=max_states, max_depth=max_depth)
    return {
        "passed": not rollout["errors"],
        "errors": rollout["errors"],
        "warnings": rollout["warnings"],
        "states_checked": len(rollout["states"]),
        "transitions_checked": len(rollout["transitions"]),
        "rollout": rollout,
    }


def execute_generated_posg(source: str) -> Dict[str, Any]:
    """Execute generated code and return a structured result instead of raising downstream."""
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return {
            "success": False,
            "stage": "syntax",
            "errors": [f"SyntaxError: {error}"],
            "world_model": None,
        }
    if any(isinstance(node, ast.ClassDef) and node.name == "AbstractPOSG" for node in tree.body):
        return {
            "success": False,
            "stage": "interface",
            "errors": ["Generated code must use the provided AbstractPOSG, not redefine it."],
            "world_model": None,
        }
    namespace: Dict[str, Any] = {
        "AbstractPOSG": AbstractPOSG,
        "Any": Any,
        "Dict": Dict,
        "List": List,
        "Mapping": Mapping,
        "Optional": Optional,
    }
    try:
        exec(source, namespace)
    except Exception as error:
        return {
            "success": False,
            "stage": "execution",
            "errors": [f"{type(error).__name__}: {error}"],
            "world_model": None,
        }
    generated_class = namespace.get("GeneratedPOSG")
    if not isinstance(generated_class, type):
        return {
            "success": False,
            "stage": "class_lookup",
            "errors": ["GeneratedPOSG class was not defined."],
            "world_model": None,
        }
    try:
        world_model = generated_class()
    except Exception as error:
        return {
            "success": False,
            "stage": "instantiation",
            "errors": [f"{type(error).__name__}: {error}"],
            "world_model": None,
        }
    return {
        "success": True,
        "stage": "execution",
        "errors": [],
        "world_model": world_model,
        "namespace": namespace,
    }


def run_posg_experiment(
    game_description: str,
    *,
    model_name: str,
    code_generator: Any,
    max_states: int = 1_000,
    max_depth: int = 20,
) -> Dict[str, Any]:
    """Run generation, execution, exhaustive validation, rollout, and EDA.

    ``code_generator`` receives ``(game_description, model_name)`` and returns Python source.
    It is injected so the research pipeline remains testable without an LLM service.
    """
    try:
        source = code_generator(game_description, model_name)
    except Exception as error:
        return {
            "success": False,
            "stage": "generation",
            "errors": [f"{type(error).__name__}: {error}"],
            "generated_code": None,
        }
    execution = execute_generated_posg(source)
    if not execution["success"]:
        return {**execution, "generated_code": source}
    validation = validate_posg(
        execution["world_model"], max_states=max_states, max_depth=max_depth
    )
    if not validation["passed"]:
        return {
            "success": False,
            "stage": "validation",
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "generated_code": source,
            "world_model": execution["world_model"],
            "validation": validation,
        }
    rollout = validation["rollout"]
    from .eda import WorldModelEDA

    eda = WorldModelEDA.from_rollout(rollout)
    return {
        "success": True,
        "stage": "complete",
        "errors": [],
        "warnings": validation["warnings"],
        "generated_code": source,
        "world_model": execution["world_model"],
        "validation": validation,
        "rollout": rollout,
        "state_graph": build_state_graph(rollout),
        "state_action_graph": build_state_action_graph(rollout),
        "eda": eda,
        "eda_summary": eda.summary(),
        "player_action_statistics": player_action_statistics(rollout),
        "action_influence": action_influence(rollout),
        "world_model_summary": summarize_rollout(rollout),
        "canonical_world_model_json": canonical_rollout_json(rollout),
    }


def build_state_graph(rollout: Mapping[str, Any]) -> nx.DiGraph:
    """Build a state graph while retaining all action/probability metadata on edges."""
    graph = nx.DiGraph()
    for state, metadata in rollout["states"].items():
        graph.add_node(state, **metadata)
    for record in rollout["transitions"]:
        for outcome in record["outcomes"]:
            source, target = record["state"], outcome["next_state"]
            if not graph.has_edge(source, target):
                graph.add_edge(source, target, transitions=[])
            graph.edges[source, target]["transitions"].append(
                {
                    "joint_action": dict(record["joint_action"]),
                    "probability": outcome["probability"],
                }
            )
    return graph


def build_state_action_graph(rollout: Mapping[str, Any]) -> nx.DiGraph:
    """Build a bipartite state-action-transition representation."""
    graph = nx.DiGraph()
    for state, metadata in rollout["states"].items():
        graph.add_node(state, node_type="state", **metadata)
    for index, record in enumerate(rollout["transitions"]):
        action_node = ("action", index)
        graph.add_node(
            action_node,
            node_type="action",
            joint_action=dict(record["joint_action"]),
            label=" | ".join(f"{player}={action}" for player, action in record["joint_action"].items()),
        )
        graph.add_edge(record["state"], action_node)
        for outcome in record["outcomes"]:
            graph.add_edge(action_node, outcome["next_state"], probability=outcome["probability"])
    return graph


def player_action_statistics(rollout: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Summarize player action availability across reachable non-terminal states."""
    statistics: Dict[str, Dict[str, Any]] = {}
    for player in rollout["players"]:
        counts = [
            len(actions[player])
            for actions in rollout["actions"].values()
            if player in actions
        ]
        statistics[player] = {
            "states_where_player_can_act": len(counts),
            "action_counts_by_state": {
                state: len(actions[player])
                for state, actions in rollout["actions"].items()
                if player in actions
            },
            "average_action_branching": sum(counts) / len(counts) if counts else None,
            "maximum_action_branching": max(counts, default=0),
        }
    return statistics


def action_influence(rollout: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Compare transition distributions when one player's action changes.

    The returned total-variation distances are structural descriptors, not power metrics.
    """
    by_state_action = {
        (record["state"], tuple(record["joint_action"].items())): record["outcomes"]
        for record in rollout["transitions"]
    }
    results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for state, actions in rollout["actions"].items():
        players = list(actions)
        for player in players:
            other_players = [other for other in players if other != player]
            for other_values in itertools.product(*(actions[other] for other in other_players)):
                distributions = {}
                for action in actions[player]:
                    joint_action = {
                        **dict(zip(other_players, other_values)),
                        player: action,
                    }
                    ordered = tuple((name, joint_action[name]) for name in rollout["players"])
                    outcomes = by_state_action.get((state, ordered), [])
                    distributions[action] = {
                        outcome["next_state"]: outcome["probability"] for outcome in outcomes
                    }
                for first, second in itertools.combinations(distributions, 2):
                    support = set(distributions[first]) | set(distributions[second])
                    distance = 0.5 * sum(
                        abs(distributions[first].get(next_state, 0.0) - distributions[second].get(next_state, 0.0))
                        for next_state in support
                    )
                    results[player].append(
                        {
                            "state": state,
                            "other_actions": dict(zip(other_players, other_values)),
                            "actions_compared": (first, second),
                            "total_variation_distance": distance,
                        }
                    )
    return dict(results)
