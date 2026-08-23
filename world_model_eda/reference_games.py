"""Executable reference fixtures for running the Python rollout pipeline on G1-G9.

These fixtures interpret the repository's expected declarative schemas. They are for
pipeline integration checks, not substitutes for LLM-generated Python world models.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List

from .python_posg import AbstractPOSG


def load_game_schema(path: str | Path) -> Dict[str, Any]:
    """Extract the first expected-output JSON object from a game-case Markdown file."""
    text = Path(path).read_text(encoding="utf-8")
    marker = text.find("Expected LLM Output")
    if marker < 0:
        raise ValueError(f"{path} has no expected-output section.")
    start = text.find("{", marker)
    if start < 0:
        raise ValueError(f"{path} has no expected-output JSON.")
    return json.JSONDecoder().raw_decode(text[start:])[0]


class SchemaPOSG(AbstractPOSG):
    """Adapt an expected game-case schema into an executable Python POSG fixture."""

    def __init__(self, schema: Dict[str, Any]) -> None:
        self.schema = schema
        self._active_players = {state: list(actions) for state, actions in schema.get("actions", {}).items()}
        declared = [player["id"] for player in schema["players"]]
        extras = [player for actions in self._active_players.values() for player in actions if player not in declared]
        self._players = declared + list(dict.fromkeys(extras))

    @property
    def players(self) -> List[str]:
        return self._players

    def initial_state(self) -> str:
        return self.schema["initial_state"]

    def legal_actions(self, state: str, player: str) -> List[str]:
        if self.is_terminal(state):
            return []
        actions = self.schema.get("actions", {}).get(state, {})
        return list(actions[player]) if player in actions else ["__inactive__"]

    def transition(self, state: str, joint_action: Dict[str, str]) -> Dict[str, float]:
        active_players = self._active_players.get(state, [])
        if any(joint_action[player] != "__inactive__" for player in self.players if player not in active_players):
            raise ValueError("Inactive players must use __inactive__.")
        encoded = "+".join(joint_action[player] for player in active_players)
        distribution = {
            next_state: float(probability)
            for next_state, probability in self.schema["transition_probabilities"][state][encoded].items()
        }
        total = sum(distribution.values())
        # The G2 Markdown schema documents rounded probabilities (0.4167 + 0.4167 +
        # 0.1667 = 1.0001). Normalize only this reference-fixture representation;
        # generated Python models remain subject to strict rollout validation.
        if not math.isclose(total, 1.0, abs_tol=1e-3):
            raise ValueError(f"Reference schema probabilities sum to {total}, not 1.0.")
        return {next_state: probability / total for next_state, probability in distribution.items()}

    def observation(self, state: str, joint_action: Dict[str, str], next_state: str, player: str) -> str:
        return f"transitioned_to:{next_state}"

    def reward(self, state: str, joint_action: Dict[str, str], next_state: str, player: str) -> float:
        state_reward = self.schema["states"][next_state].get("reward", {})
        if player in state_reward:
            return float(state_reward[player])
        active_players = self._active_players.get(state, [])
        encoded = "+".join(joint_action[active] for active in active_players)
        return float(self.schema.get("rewards", {}).get(state, {}).get(encoded, {}).get(player, 0.0))

    def is_terminal(self, state: str) -> bool:
        return bool(self.schema["states"][state].get("terminal", False))


def load_reference_game_cases(root: str | Path) -> Dict[str, SchemaPOSG]:
    """Load G1-G9 executable reference fixtures from the existing Markdown cases."""
    directory = Path(root)
    cases = {}
    for path in sorted(directory.glob("game_G_*.md")):
        number = int(path.name.split("_")[2])
        cases[f"G{number}"] = SchemaPOSG(load_game_schema(path))
    return cases
