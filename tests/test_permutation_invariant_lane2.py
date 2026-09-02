"""Sanity tests for the pinned permutation-invariant Lane-2 matcher."""

from __future__ import annotations

import copy
import unittest

from json_generation.lane2 import lane2_score


def fixture() -> dict:
    return {
        "players": [{"id": "row"}, {"id": "column"}],
        "initial": [{"state": "start", "p": 1.0}],
        "states": [
            {
                "id": "start",
                "terminal": False,
                "turn": ["row", "column"],
                "actions": [
                    {"by": {"row": "up", "column": "left"}, "next": [{"state": "win", "p": 1.0}]},
                    {"by": {"row": "up", "column": "right"}, "next": [{"state": "lose", "p": 1.0}]},
                    {"by": {"row": "down", "column": "left"}, "next": [{"state": "lose", "p": 1.0}]},
                    {"by": {"row": "down", "column": "right"}, "next": [{"state": "win", "p": 1.0}]},
                ],
            },
            {"id": "win", "terminal": True},
            {"id": "lose", "terminal": True},
        ],
    }


def rename(model: dict, states: dict[str, str], players: dict[str, str]) -> dict:
    result = copy.deepcopy(model)
    for entry in result["initial"]:
        entry["state"] = states[entry["state"]]
    for player in result["players"]:
        player["id"] = players[player["id"]]
    for state in result["states"]:
        state["id"] = states[state["id"]]
        state["turn"] = [players[p] for p in state.get("turn", [])]
        for action in state.get("actions", []):
            action["by"] = {players[p]: f"renamed_{a}" for p, a in action["by"].items()}
            for successor in action["next"]:
                successor["state"] = states[successor["state"]]
    return result


class PermutationInvariantLane2Tests(unittest.TestCase):
    def score(self, candidate: dict) -> dict:
        return lane2_score(fixture(), candidate, horizon=2, sa_iters=1_000, seed=7)

    def test_identical_and_reordered_states_are_exact(self) -> None:
        self.assertEqual(self.score(fixture())["lane2"], 1.0)
        reordered = fixture()
        reordered["states"] = list(reversed(reordered["states"]))
        self.assertEqual(self.score(reordered)["lane2"], 1.0)

    def test_state_action_and_player_renaming_is_exact(self) -> None:
        candidate = rename(
            fixture(),
            {"start": "q9", "win": "q2", "lose": "q7"},
            {"row": "agent_b", "column": "agent_a"},
        )
        result = self.score(candidate)
        self.assertEqual(result["lane2"], 1.0)
        self.assertEqual(len(result["player_map"]), 2)

    def test_missing_transition_support_lowers_score(self) -> None:
        candidate = fixture()
        candidate["states"][0]["actions"][0]["next"] = [
            {"state": "win", "p": 0.5}, {"state": "lose", "p": 0.5}
        ]
        self.assertLess(self.score(candidate)["lane2"], 1.0)

    def test_additional_action_profile_lowers_precision(self) -> None:
        candidate = fixture()
        for state in (candidate["states"][0],):
            for action in state["actions"]:
                if action["by"]["row"] == "down":
                    action["by"]["row"] = "middle"
            state["actions"].extend([
                {"by": {"row": "down", "column": "left"}, "next": [{"state": "win", "p": 1.0}]},
                {"by": {"row": "down", "column": "right"}, "next": [{"state": "lose", "p": 1.0}]},
            ])
        result = self.score(candidate)
        self.assertLess(result["precision"], 1.0)
        self.assertLess(result["lane2"], 1.0)

    def test_altered_terminality_lowers_score(self) -> None:
        candidate = fixture()
        candidate["states"][1] = {
            "id": "win", "terminal": False, "turn": ["row"],
            "actions": [{"by": {"row": "stop"}, "next": [{"state": "lose", "p": 1.0}]}],
        }
        self.assertLess(self.score(candidate)["lane2"], 1.0)

    def test_altered_probability_lowers_score(self) -> None:
        reference = fixture()
        reference["states"][0]["actions"][0]["next"] = [
            {"state": "win", "p": 0.5}, {"state": "lose", "p": 0.5}
        ]
        candidate = copy.deepcopy(reference)
        candidate["states"][0]["actions"][0]["next"] = [
            {"state": "win", "p": 0.75}, {"state": "lose", "p": 0.25}
        ]
        result = lane2_score(reference, candidate, horizon=2, sa_iters=1_000, seed=7)
        self.assertLess(result["lane2"], 1.0)

    def test_spurious_reverse_edge_lowers_score(self) -> None:
        candidate = fixture()
        candidate["states"][1] = {"id": "win", "terminal": False, "turn": ["row"],
                                  "actions": [{"by": {"row": "return"}, "next": [{"state": "start", "p": 1.0}]}]}
        self.assertLess(self.score(candidate)["lane2"], 1.0)

    def test_omitted_action_lowers_score(self) -> None:
        candidate = fixture()
        candidate["states"][0]["actions"] = candidate["states"][0]["actions"][:2]
        self.assertLess(self.score(candidate)["lane2"], 1.0)


if __name__ == "__main__":
    unittest.main()
