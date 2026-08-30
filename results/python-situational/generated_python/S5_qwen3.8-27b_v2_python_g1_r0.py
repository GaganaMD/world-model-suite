from posg import POSG

from collections.abc import Mapping, Sequence, Iterator
from typing import Generic, TypeVar, Tuple

S = TypeVar("S")
A = TypeVar("A")
O = TypeVar("O")


class WarehouseForkliftChild(POSG):
    """
    Player 0: warehouse robot operating a forklift.
    Player 1: the small child near the loading dock.

    State tuple: (child_present, child_moving)
      - child_present: True if the child is still in the vicinity of the dock, False if gone.
      - child_moving:  True if the child is currently walking away, False if standing still.

    Terminal when the child is no longer present.
    """

    n_players = 2

    # ---- helpers -------------------------------------------------------------

    def _obs(self, s):
        child_present, child_moving = s
        if not child_present:
            return ("gone", "gone")
        if child_moving:
            return ("moving", "moving")
        return ("standing", "standing")

    # ---- required methods ----------------------------------------------------

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        s0 = (True, False)
        return {(s0, self._obs(s0)): 1.0}

    def is_terminal(self, s: S) -> bool:
        return not s[0]

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("proceed", "stop")
        else:
            return ("stand_still", "walk_away")

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        if self.is_terminal(s):
            return {(s, self._obs(s)): 1.0}

        robot_act, child_act = a
        _, child_moving = s

        if child_act == "walk_away":
            # Child leaves the vicinity.
            ns = (False, False)
            return {(ns, self._obs(ns)): 1.0}

        # Child stands still.
        if robot_act == "proceed":
            # Robot moves forward; child remains.
            ns = (True, False)
            return {(ns, self._obs(ns)): 1.0}
        else:  # stop
            # Robot halts; child remains standing.
            ns = (True, False)
            return {(ns, self._obs(ns)): 1.0}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
