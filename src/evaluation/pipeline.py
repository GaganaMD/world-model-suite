"""Unified three-lane POSG evaluation and artifact persistence."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Mapping

import networkx as nx

from .lane1_mechanical import build_transition_graph, evaluate_mechanical
from .lane2_structural import evaluate_structural
from .lane3_qualitative import evaluate_qualitative


ModelInput = str | Path | Mapping[str, Any]


def _load_model(value: ModelInput, name: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    path = Path(value)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"{name} JSON not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"{name} is not valid JSON: {path}: {error}") from error
    if not isinstance(loaded, dict):
        raise ValueError(f"{name} must contain a top-level JSON object")
    return loaded


def normalize_identifiers(model: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return a copy with string player/state/action/observation identifiers."""
    normalized = copy.deepcopy(dict(model))
    coercions: list[str] = []
    for player in normalized.get("players", []) or []:
        if isinstance(player, dict) and "id" in player and not isinstance(player["id"], str):
            coercions.append(f"player id {player['id']!r} -> {str(player['id'])!r}")
            player["id"] = str(player["id"])
    for entry in normalized.get("initial", []) or []:
        if isinstance(entry, dict) and "state" in entry:
            entry["state"] = str(entry["state"])
    for state in normalized.get("states", []) or []:
        if not isinstance(state, dict):
            continue
        if "id" in state:
            original = state["id"]
            state["id"] = str(original)
            if original != state["id"]:
                coercions.append(f"state id {original!r} -> {state['id']!r}")
        if isinstance(state.get("turn"), list):
            state["turn"] = [str(player) for player in state["turn"]]
        for action in state.get("actions", []) or []:
            if not isinstance(action, dict):
                continue
            if isinstance(action.get("by"), dict):
                action["by"] = {str(player): str(identifier) for player, identifier in action["by"].items()}
            for successor in action.get("next", []) or []:
                if isinstance(successor, dict) and "state" in successor:
                    successor["state"] = str(successor["state"])
                if isinstance(successor, dict) and "observations" in successor:
                    observations = successor["observations"]
                    if isinstance(observations, dict):
                        successor["observations"] = {
                            str(player): str(observation) for player, observation in observations.items()
                        }
                    else:
                        successor["observations"] = str(observations)
    return normalized, coercions


def _graph_payload(graph: nx.DiGraph, model: Mapping[str, Any]) -> dict[str, Any]:
    import torch

    nodes = sorted(str(node) for node in graph.nodes)
    index = {node: position for position, node in enumerate(nodes)}
    adjacency = torch.zeros((len(nodes), len(nodes)), dtype=torch.float32)
    edges = []
    for source, target in graph.edges:
        source_id, target_id = str(source), str(target)
        adjacency[index[source_id], index[target_id]] = 1.0
        edges.append((source_id, target_id))
    return {
        "format": "world-model-suite.posg-graph.v1",
        "node_ids": nodes,
        "edges": edges,
        "adjacency": adjacency,
        "model": copy.deepcopy(dict(model)),
    }


class EvaluationPipeline:
    def __init__(self, output_dir: str | Path = "./evaluation_results") -> None:
        self.output_dir = Path(output_dir)

    def evaluate(
        self,
        candidate_model_path: ModelInput,
        ground_truth_path: ModelInput | None = None,
        *,
        save_pth: bool = True,
    ) -> dict[str, Any]:
        candidate_raw = _load_model(candidate_model_path, "candidate_model_path")
        ground_truth_raw = _load_model(ground_truth_path, "ground_truth_path") if ground_truth_path is not None else None
        candidate, candidate_coercions = normalize_identifiers(candidate_raw)
        ground_truth, truth_coercions = (
            normalize_identifiers(ground_truth_raw) if ground_truth_raw is not None else (None, [])
        )

        os.makedirs(self.output_dir, exist_ok=True)
        lane1 = evaluate_mechanical(candidate)
        lane2 = evaluate_structural(candidate, ground_truth)
        lane3 = evaluate_qualitative(candidate, ground_truth)
        lane1["details"]["identifier_coercions"] = candidate_coercions
        lane2["details"]["ground_truth_identifier_coercions"] = truth_coercions

        saved_artifacts: list[str] = []
        if save_pth:
            try:
                import torch
            except ImportError as error:
                raise RuntimeError("save_pth=True requires PyTorch; install torch or pass save_pth=False") from error
            candidate_path = self.output_dir / "candidate_graph.pth"
            torch.save(_graph_payload(build_transition_graph(candidate), candidate), candidate_path)
            saved_artifacts.append(str(candidate_path.resolve()))
            if ground_truth is not None:
                truth_path = self.output_dir / "ground_truth_graph.pth"
                torch.save(_graph_payload(build_transition_graph(ground_truth), ground_truth), truth_path)
                saved_artifacts.append(str(truth_path.resolve()))

        report = {
            "lane1": lane1,
            "lane2": lane2,
            "lane3": lane3,
            "overall_passed": bool(
                lane1["passed"]
                and lane3["checklist_passed"]
                and (ground_truth is None or lane2["combined_score"] > 0.0)
            ),
            "saved_artifacts": saved_artifacts,
        }
        report_path = self.output_dir / "evaluation_report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return report


def evaluate_world_model(
    candidate_model_path: ModelInput,
    ground_truth_path: ModelInput | None = None,
    save_pth: bool = True,
    output_dir: str = "./evaluation_results",
) -> dict[str, Any]:
    """Evaluate a candidate across all lanes and return the requested result schema."""
    return EvaluationPipeline(output_dir).evaluate(
        candidate_model_path,
        ground_truth_path,
        save_pth=save_pth,
    )

