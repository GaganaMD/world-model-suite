from posg import POSG

from typing import Mapping, Sequence
import random
from abc import ABC, abstractmethod

class POSG(ABC):
    # Provided abstract class – do not redefine.
    ...

class FactorySafetyPOSG(POSG[str, str, str]):
    """
    Player 0: Robot.
    Player 1: Human coworker.

    State is a string representing the current phase of the interaction:
        'initial'          – human chooses lockout or skip, robot waits.
        'post_lockout'     – human locked out, robot chooses intervene/ignore.
        'post_skip'        – human skipped, robot chooses intervene/ignore.
        'safe_terminal'    – outcome: no accident.
        'accident_terminal'– outcome: accident.
    """
    n_players = 2

    # ── state identifiers ──────────────────────────────────────────────
    INITIAL          = "initial"
    POST_LOCKOUT     = "post_lockout"
    POST_SKIP        = "post_skip"
    SAFE_TERMINAL    = "safe_terminal"
    ACCIDENT_TERMINAL= "accident_terminal"

    # ── abstract methods ──────────────────────────────────────────────
    def initial_distribution(self) -> Mapping[tuple[str, tuple[str, str]], float]:
        return {(self.INITIAL, ("none", "none")): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s in (self.SAFE_TERMINAL, self.ACCIDENT_TERMINAL)

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == self.INITIAL:
            return ("wait",) if i == 0 else ("lockout", "skip")
        if s in (self.POST_LOCKOUT, self.POST_SKIP):
            return ("intervene", "ignore") if i == 0 else ("noop",)
        return ()   # terminal – not called

    def transition(self,
                   s: str,
                   a: tuple[str, str]
                   ) -> Mapping[tuple[str, tuple[str, str]], float]:
        robot_act, human_act = a

        if s == self.INITIAL:
            # human acts, robot waits
            if human_act == "lockout":
                return {(self.POST_LOCKOUT, ("lockout", "none")): 1.0}
            else:  # skip
                return {(self.POST_SKIP,   ("skip",    "none")): 1.0}

        if s == self.POST_LOCKOUT:
            # robot acts, human noop
            if robot_act == "intervene":
                return {(self.SAFE_TERMINAL, ("safe", "intervened")): 1.0}
            else:  # ignore
                return {(self.SAFE_TERMINAL, ("safe", "none"      )): 1.0}

        if s == self.POST_SKIP:
            if robot_act == "intervene":
                return {(self.SAFE_TERMINAL, ("safe", "intervened")): 1.0}
            else:  # ignore – 10 % chance of accident
                return {(self.SAFE_TERMINAL,     ("safe",    "none"     )): 0.9,
                        (self.ACCIDENT_TERMINAL, ("accident", "accident")): 0.1}

        # terminal states have no outgoing transition
        return {}

    def rewards(self,
                s: str,
                a: tuple[str, str],
                s_next: str
                ) -> tuple[float, ...]:
        return (0.0, 0.0)
