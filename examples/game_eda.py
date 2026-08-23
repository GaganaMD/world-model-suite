"""Run graph EDA for the G1 Rock-Paper-Scissors and G2 Dice Duel schemas."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from world_model_eda import WorldModelEDA


RPS = {
    "players": [{"id": "player_1"}, {"id": "player_2"}],
    "initial_state": "s0",
    "states": {
        "s0": {"terminal": False},
        "p1_wins": {"terminal": True},
        "p2_wins": {"terminal": True},
        "draw": {"terminal": True},
    },
    "actions": {
        "s0": {
            "player_1": ["rock", "paper", "scissors"],
            "player_2": ["rock", "paper", "scissors"],
        }
    },
    "transition_probabilities": {
        "s0": {
            "rock+rock": {"draw": 1.0},
            "rock+paper": {"p2_wins": 1.0},
            "rock+scissors": {"p1_wins": 1.0},
            "paper+rock": {"p1_wins": 1.0},
            "paper+paper": {"draw": 1.0},
            "paper+scissors": {"p2_wins": 1.0},
            "scissors+rock": {"p2_wins": 1.0},
            "scissors+paper": {"p1_wins": 1.0},
            "scissors+scissors": {"draw": 1.0},
        }
    },
}


if __name__ == "__main__":
    analysis = WorldModelEDA.from_dict(RPS)
    print(analysis.summary())
