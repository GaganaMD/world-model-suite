from posg import POSG

from typing import Mapping, Sequence, Tuple

class FactoryRobot(POSG):
    """
    Players:
      index 0: factory robot
      index 1: human coworker

    State: a tuple of length 1 whose first element is a string token.
      - "pre_reach": the human is about to reach into the machine.
      - "post_reach": the human has already reached into the machine (terminal).
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[Tuple[str, ...], Tuple[str, str]], float]:
        # Initially nobody has observed anything.
        return {(("pre_reach",), ("none", "none")): 1.0}

    def is_terminal(self, s: Tuple[str, ...]) -> bool:
        return s[0] == "post_reach"

    def legal_actions(self, s: Tuple[str, ...], i: int) -> Sequence[str]:
        if s[0] == "pre_reach":
            if i == 0:
                return ("observe",)
            else:
                return ("skip_lockout",)
        # Terminal state – should not be called, but provide a safe fallback.
        return ("noop",)

    def transition(self, s: Tuple[str, ...], a: Tuple[str, ...]) -> Mapping[tuple[Tuple[str, ...], Tuple[str, str]], float]:
        # a[0] = robot action, a[1] = human action (both ignored – only one possible)
        s_next = ("post_reach",)
        obs = ("skip_observed", "none")
        return {(s_next, obs): 1.0}

    def rewards(self, s: Tuple[str, ...], a: Tuple[str, ...], s_next: Tuple[str, ...]) -> Tuple[float, float]:
        return (0.0, 0.0)
