from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
import random
from abc import ABC, abstractmethod

# Base class is provided externally; we assume it exists.
# We'll define our subclass below.

class ElderCareRobotPOSG(POSG[int, str, str]):
    """
    Players:
      - Player 0: elder-care robot
      - Player 1: resident

    States (int):
      0: medication not taken, robot has not yet reminded
      1: robot has reminded, resident has not yet responded
      2: medication taken (terminal)
      3: resident refused and turned away (terminal)

    Actions:
      Robot: "remind", "noop"
      Resident: "noop", "take", "refuse"

    Observations:
      Robot: "not_taken", "none", "taken", "refused"
      Resident: "none", "reminder"
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[int, Tuple[str, str]], float]:
        return {(0, ("not_taken", "none")): 1.0}

    def is_terminal(self, s: int) -> bool:
        return s in (2, 3)

    def legal_actions(self, s: int, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)  # both players noop in terminal states
        if s == 0:            # initial state
            if i == 0:
                return ("remind",)
            else:  # i == 1
                return ("noop",)
        if s == 1:            # reminded state
            if i == 0:
                return ("noop",)
            else:  # i == 1
                return ("take", "refuse")
        # Should never reach here
        raise ValueError(f"Unknown state {s}")

    def transition(self, s: int, a: Tuple[str, str]) -> Mapping[Tuple[int, Tuple[str, str]], float]:
        if s == 0 and a == ("remind", "noop"):
            return {(1, ("none", "reminder")): 1.0}
        if s == 1:
            if a == ("noop", "take"):
                return {(2, ("taken", "none")): 1.0}
            if a == ("noop", "refuse"):
                return {(3, ("refused", "none")): 1.0}
        # Fallback for terminal or impossible profiles
        return {(s, ("none", "none")): 1.0}

    def rewards(self, s: int, a: Tuple[str, str], s_next: int) -> Tuple[float, ...]:
        return (0.0, 0.0)
