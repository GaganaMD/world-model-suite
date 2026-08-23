"""Graph-focused exploratory analysis for finite POSG world models."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import product
from math import log2
from typing import Any, Dict, Hashable, Iterable, Mapping, Optional, Sequence

import networkx as nx


@dataclass(frozen=True)
class Transition:
    """One possible outcome of a state and joint action."""

    state: Hashable
    actions: tuple[tuple[str, str], ...]
    next_state: Hashable
    probability: float

    @property
    def action_label(self) -> str:
        return " + ".join(f"{player}:{action}" for player, action in self.actions)


class WorldModelEDA:
    """Extract, graph, and summarize a finite POSG without evaluating correctness.

    Use :meth:`from_dict` for the JSON-like schema used by the game test cases, or
    :meth:`from_posg` for an object implementing the notebook's ``AbstractPOSG``
    interface.  The latter enumerates states reachable from ``initial_state``.
    """

    def __init__(
        self,
        states: Iterable[Hashable],
        terminal_states: Iterable[Hashable],
        transitions: Iterable[Transition],
        actions_by_state: Mapping[Hashable, Sequence[tuple[tuple[str, str], ...]]],
        initial_state: Optional[Hashable] = None,
    ) -> None:
        self.states = set(states)
        self.terminal_states = set(terminal_states)
        self.transitions = list(transitions)
        self.actions_by_state = {
            state: list(actions) for state, actions in actions_by_state.items()
        }
        self.initial_state = initial_state
        self.states.update(self.terminal_states)
        for transition in self.transitions:
            self.states.update((transition.state, transition.next_state))

    @classmethod
    def from_dict(cls, model: Mapping[str, Any]) -> "WorldModelEDA":
        """Build an analysis from the declarative game-case JSON schema."""
        state_metadata = model["states"]
        states = list(state_metadata)
        terminal_states = [
            state for state, metadata in state_metadata.items() if metadata.get("terminal", False)
        ]
        players = [player["id"] if isinstance(player, Mapping) else player for player in model["players"]]
        actions_by_state: Dict[Hashable, list[tuple[tuple[str, str], ...]]] = {}
        transitions: list[Transition] = []

        for state, action_sets in model.get("actions", {}).items():
            joint_actions = [
                tuple(zip(players, choices))
                for choices in product(*(action_sets.get(player, []) for player in players))
            ]
            actions_by_state[state] = joint_actions

        for state, action_outcomes in model.get("transition_probabilities", {}).items():
            for encoded_action, outcomes in action_outcomes.items():
                action_values = encoded_action.split("+")
                if len(action_values) != len(players):
                    raise ValueError(
                        f"Joint action {encoded_action!r} in {state!r} has {len(action_values)} "
                        f"actions for {len(players)} players."
                    )
                actions = tuple(zip(players, action_values))
                for next_state, probability in outcomes.items():
                    transitions.append(
                        Transition(state, actions, next_state, float(probability))
                    )

        return cls(
            states,
            terminal_states,
            transitions,
            actions_by_state,
            model.get("initial_state"),
        )

    @classmethod
    def from_posg(cls, posg: Any, max_states: int = 10_000) -> "WorldModelEDA":
        """Enumerate the reachable portion of an ``AbstractPOSG`` implementation."""
        players = tuple(posg.players)
        initial_state = posg.initial_state
        states = {initial_state}
        terminal_states = set()
        queue = deque([initial_state])
        actions_by_state: Dict[Hashable, list[tuple[tuple[str, str], ...]]] = {}
        transitions: list[Transition] = []

        while queue:
            state = queue.popleft()
            if posg.is_terminal(state):
                terminal_states.add(state)
                continue
            joint_actions = [
                tuple(zip(players, choices))
                for choices in product(*(posg.legal_actions(state, player) for player in players))
            ]
            actions_by_state[state] = joint_actions
            for actions in joint_actions:
                outcome_probabilities: Dict[Hashable, float] = defaultdict(float)
                for (next_state, _observation), probability in posg.transition_kernel(
                    state, dict(actions)
                ).items():
                    outcome_probabilities[next_state] += float(probability)
                for next_state, probability in outcome_probabilities.items():
                    transitions.append(Transition(state, actions, next_state, probability))
                    if next_state not in states:
                        if len(states) >= max_states:
                            raise ValueError(f"Reachable state limit ({max_states}) exceeded.")
                        states.add(next_state)
                        queue.append(next_state)

        return cls(states, terminal_states, transitions, actions_by_state, initial_state)

    def extract_states(self) -> list[Hashable]:
        """Return all represented states."""
        return sorted(self.states, key=repr)

    def extract_actions(self) -> Dict[Hashable, list[Dict[str, str]]]:
        """Return available joint actions for every represented state."""
        return {
            state: [dict(actions) for actions in actions]
            for state, actions in self.actions_by_state.items()
        }

    def extract_transitions(self) -> list[Dict[str, Any]]:
        """Return transitions in a tabular, serialization-friendly form."""
        return [
            {
                "state": transition.state,
                "actions": dict(transition.actions),
                "next_state": transition.next_state,
                "probability": transition.probability,
            }
            for transition in self.transitions
        ]

    def _outcomes(self) -> Dict[tuple[Hashable, tuple[tuple[str, str], ...]], list[Transition]]:
        outcomes: Dict[tuple[Hashable, tuple[tuple[str, str], ...]], list[Transition]] = defaultdict(list)
        for transition in self.transitions:
            outcomes[(transition.state, transition.actions)].append(transition)
        return outcomes

    def build_state_graph(self) -> nx.DiGraph:
        """Build a directed state graph with probability and action metadata."""
        graph = nx.DiGraph()
        graph.add_nodes_from((state, {"terminal": state in self.terminal_states}) for state in self.states)
        edge_data: Dict[tuple[Hashable, Hashable], Dict[str, Any]] = {}
        for transition in self.transitions:
            key = (transition.state, transition.next_state)
            data = edge_data.setdefault(key, {"probability": 0.0, "actions": []})
            data["probability"] += transition.probability
            data["actions"].append(transition.action_label)
        graph.add_edges_from((source, target, data) for (source, target), data in edge_data.items())
        return graph

    def build_state_action_graph(self) -> nx.DiGraph:
        """Build a bipartite graph of states, joint actions, and successor states."""
        graph = nx.DiGraph()
        for state in self.states:
            graph.add_node(state, node_type="state", terminal=state in self.terminal_states)
        for (state, actions), outcomes in self._outcomes().items():
            action_node = ("action", state, actions)
            graph.add_node(action_node, node_type="action", label=self._action_label(actions))
            graph.add_edge(state, action_node)
            for transition in outcomes:
                graph.add_edge(
                    action_node,
                    transition.next_state,
                    probability=transition.probability,
                )
        return graph

    def build_player_action_state_graph(self) -> nx.DiGraph:
        """Build a graph exposing each player's action-specific influence."""
        graph = nx.DiGraph()
        for transition in self.transitions:
            for player, action in transition.actions:
                player_node = ("player", player)
                action_node = ("player_action", player, action)
                graph.add_edge(player_node, action_node)
                graph.add_edge(action_node, transition.state)
                graph.add_edge(
                    action_node,
                    transition.next_state,
                    probability=transition.probability,
                )
        return graph

    def state_statistics(self) -> Dict[str, Any]:
        """Calculate state-space size, terminal depth, and branching statistics."""
        graph = self.build_state_graph()
        branch_counts = [len(self.actions_by_state.get(state, [])) for state in self.states]
        depths = self._terminal_distances(graph)
        finite_depths = [depth for depth in depths.values() if depth is not None]
        return {
            "state_count": len(self.states),
            "terminal_state_count": len(self.terminal_states),
            "non_terminal_state_count": len(self.states - self.terminal_states),
            "terminal_to_non_terminal_ratio": (
                len(self.terminal_states) / len(self.states - self.terminal_states)
                if self.states - self.terminal_states else None
            ),
            "reachable_state_count": len(self.states),
            "maximum_depth_to_terminal": max(finite_depths, default=None),
            "average_depth_to_terminal": self._mean(finite_depths),
            "branching_factor_by_state": dict(zip(self.states, branch_counts)),
            "mean_branching_factor": self._mean(branch_counts),
            "maximum_branching_factor": max(branch_counts, default=0),
            "self_loop_count": nx.number_of_selfloops(graph),
        }

    def action_statistics(self) -> Dict[str, Any]:
        """Calculate joint-action branching, player actions, and redundancy."""
        outcomes = self._outcomes()
        joint_action_count = len(outcomes)
        players: Dict[str, set[str]] = defaultdict(set)
        for _, actions in outcomes:
            for player, action in actions:
                players[player].add(action)
        signatures = {
            tuple(sorted((repr(item.next_state), round(item.probability, 12)) for item in items))
            for items in outcomes.values()
        }
        return {
            "joint_action_count": joint_action_count,
            "unique_actions_by_player": {player: sorted(actions) for player, actions in players.items()},
            "unique_action_count": len({action for actions in players.values() for action in actions}),
            "action_redundancy": (
                (joint_action_count - len(signatures)) / joint_action_count if joint_action_count else 0.0
            ),
            "outcome_compression": len(signatures) / joint_action_count if joint_action_count else 0.0,
        }

    def transition_statistics(self) -> Dict[str, Any]:
        """Calculate successor branching, stochasticity, and transition entropy."""
        outcomes = self._outcomes()
        counts = [len(items) for items in outcomes.values()]
        entropies = [
            -sum(item.probability * log2(item.probability) for item in items if item.probability > 0)
            for items in outcomes.values()
        ]
        deterministic = sum(count == 1 for count in counts)
        return {
            "state_action_pair_count": len(outcomes),
            "average_transition_branching": self._mean(counts),
            "maximum_transition_branching": max(counts, default=0),
            "deterministic_transition_fraction": deterministic / len(counts) if counts else 0.0,
            "stochastic_transition_fraction": (len(counts) - deterministic) / len(counts) if counts else 0.0,
            "unique_successor_state_count": len({item.next_state for item in self.transitions}),
            "mean_transition_entropy": self._mean(entropies),
            "maximum_transition_entropy": max(entropies, default=0.0),
        }

    def entropy_analysis(self) -> Dict[str, float]:
        """Return transition entropy for every state and joint-action pair."""
        return {
            f"{state!r} | {self._action_label(actions)}": -sum(
                item.probability * log2(item.probability)
                for item in outcomes
                if item.probability > 0
            )
            for (state, actions), outcomes in self._outcomes().items()
        }

    def terminal_statistics(self) -> Dict[str, Any]:
        """Return shortest transition distance from each state to a terminal state."""
        distances = self._terminal_distances(self.build_state_graph())
        return {
            "distance_to_terminal": distances,
            "states_without_terminal_path": [
                state for state, distance in distances.items() if distance is None
            ],
        }

    def graph_statistics(self) -> Dict[str, Any]:
        """Calculate directed graph metrics over the represented state graph."""
        graph = self.build_state_graph()
        components = list(nx.strongly_connected_components(graph))
        undirected = graph.to_undirected()
        communities = list(nx.community.greedy_modularity_communities(undirected)) if graph.number_of_edges() else []
        return {
            "density": nx.density(graph),
            "strongly_connected_component_count": len(components),
            "strongly_connected_components": [sorted(component, key=repr) for component in components],
            "weakly_connected_component_count": nx.number_weakly_connected_components(graph),
            "average_shortest_path_length": self._average_reachable_path_length(graph),
            "global_efficiency": self._global_efficiency(graph),
            "community_count": len(communities),
            "modularity": nx.community.modularity(undirected, communities) if communities else 0.0,
        }

    def centrality_analysis(self) -> Dict[str, Dict[Hashable, float]]:
        """Calculate node-level centrality metrics for the state graph."""
        graph = self.build_state_graph()
        return {
            "in_degree": dict(graph.in_degree()),
            "out_degree": dict(graph.out_degree()),
            "betweenness": nx.betweenness_centrality(graph),
            "closeness": nx.closeness_centrality(graph),
            "eigenvector": self._eigenvector_centrality(graph),
        }

    def plot_state_graph(self, ax: Any = None) -> Any:
        """Draw the state graph; returns the Matplotlib axes."""
        import matplotlib.pyplot as plt

        graph = self.build_state_graph()
        ax = ax or plt.subplots(figsize=(8, 6))[1]
        positions = nx.spring_layout(graph, seed=7)
        colors = ["#e76f51" if graph.nodes[node]["terminal"] else "#457b9d" for node in graph]
        nx.draw_networkx(graph, positions, node_color=colors, arrows=True, ax=ax)
        nx.draw_networkx_edge_labels(
            graph,
            positions,
            edge_labels={(u, v): ", ".join(data["actions"]) for u, v, data in graph.edges(data=True)},
            font_size=7,
            ax=ax,
        )
        ax.set_axis_off()
        return ax

    def plot_state_action_graph(self, ax: Any = None) -> Any:
        """Draw the state-action-transition graph; returns the Matplotlib axes."""
        import matplotlib.pyplot as plt

        graph = self.build_state_action_graph()
        ax = ax or plt.subplots(figsize=(10, 7))[1]
        positions = nx.spring_layout(graph, seed=7)
        colors = ["#f4a261" if graph.nodes[node]["node_type"] == "action" else "#457b9d" for node in graph]
        labels = {node: data.get("label", str(node)) for node, data in graph.nodes(data=True)}
        nx.draw_networkx(graph, positions, node_color=colors, labels=labels, arrows=True, font_size=8, ax=ax)
        ax.set_axis_off()
        return ax

    def plot_branching_distribution(self, ax: Any = None) -> Any:
        """Plot the distribution of available joint-action counts."""
        import matplotlib.pyplot as plt

        ax = ax or plt.subplots()[1]
        values = [len(self.actions_by_state.get(state, [])) for state in self.states]
        ax.hist(values, bins=range(max(values, default=0) + 2), align="left", rwidth=0.8)
        ax.set(xlabel="Joint actions available", ylabel="State count", title="Branching-factor distribution")
        return ax

    def plot_probability_distribution(self, ax: Any = None) -> Any:
        """Plot probabilities of all individual transition outcomes."""
        import matplotlib.pyplot as plt

        ax = ax or plt.subplots()[1]
        ax.hist([item.probability for item in self.transitions], bins=10)
        ax.set(xlabel="Transition probability", ylabel="Outcome count", title="Transition-probability distribution")
        return ax

    def summary(self) -> Dict[str, Any]:
        """Return all EDA families in one serialization-friendly report."""
        return {
            "states": self.state_statistics(),
            "actions": self.action_statistics(),
            "transitions": self.transition_statistics(),
            "terminal": self.terminal_statistics(),
            "graph": self.graph_statistics(),
        }

    @staticmethod
    def _action_label(actions: tuple[tuple[str, str], ...]) -> str:
        return " + ".join(f"{player}:{action}" for player, action in actions)

    @staticmethod
    def _mean(values: Sequence[float]) -> Optional[float]:
        return sum(values) / len(values) if values else None

    def _terminal_distances(self, graph: nx.DiGraph) -> Dict[Hashable, Optional[int]]:
        reverse = graph.reverse()
        distances: Dict[Hashable, int] = {}
        queue = deque((state, 0) for state in self.terminal_states)
        while queue:
            state, depth = queue.popleft()
            if state in distances:
                continue
            distances[state] = depth
            queue.extend((predecessor, depth + 1) for predecessor in reverse.neighbors(state))
        return {state: distances.get(state) for state in self.states}

    @staticmethod
    def _average_reachable_path_length(graph: nx.DiGraph) -> Optional[float]:
        lengths = [
            distance
            for source in graph
            for target, distance in nx.single_source_shortest_path_length(graph, source).items()
            if source != target
        ]
        return sum(lengths) / len(lengths) if lengths else None

    @staticmethod
    def _global_efficiency(graph: nx.DiGraph) -> float:
        count = graph.number_of_nodes()
        if count < 2:
            return 0.0
        inverse_distances = sum(
            1 / distance
            for source in graph
            for target, distance in nx.single_source_shortest_path_length(graph, source).items()
            if source != target and distance
        )
        return inverse_distances / (count * (count - 1))

    @staticmethod
    def _eigenvector_centrality(graph: nx.DiGraph) -> Dict[Hashable, float]:
        if not graph:
            return {}
        try:
            return nx.eigenvector_centrality(graph, max_iter=1_000)
        except nx.PowerIterationFailedConvergence:
            return {state: 0.0 for state in graph}
