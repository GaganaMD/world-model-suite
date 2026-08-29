from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional, Any, Union

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class WarehouseForkliftChild(POSG):
    """
    Player 0: warehouse robot (forklift operator)
    Player 1: child

    State tuple: (child_present, child_moving, child_safe)
      - child_present: bool, whether the child is still in the vicinity
      - child_moving: bool, whether the child is currently in motion
      - child_safe: bool, whether the child is clear of the forklift's path

    Terminal when child_present is False (child has left the area).
    """
    n_players = 2

    # --- helpers -----------------------------------------------------------

    def _obs_robot(self, s):
        child_present, child_moving, child_safe = s
        if not child_present:
            return "child_gone"
        if child_safe:
            return "child_clear"
        if child_moving:
            return "child_unpredictable"
        return "child_in_path"

    def _obs_child(self, s):
        child_present, child_moving, child_safe = s
        if not child_present:
            return "gone"
        if child_safe:
            return "clear"
        return "near"

    def _obs_profile(self, s):
        return (self._obs_robot(s), self._obs_child(s))

    # --- POSG interface ----------------------------------------------------

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        s0 = (True, False, False)
        return {(s0, self._obs_profile(s0)): 1.0}

    def is_terminal(self, s: S) -> bool:
        return not s[0]

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("proceed", "stop")
        else:
            return ("stay", "move")

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        if self.is_terminal(s):
            return {(s, self._obs_profile(s)): 1.0}

        robot_act, child_act = a
        child_present, child_moving, child_safe = s

        # Child leaves the area
        if child_act == "move":
            ns = (False, False, False)
            return {(ns, self._obs_profile(ns)): 1.0}

        # Child stays
        if child_act == "stay":
            if robot_act == "proceed":
                # Forklift moves toward/through the child's position
                # Child is displaced / removed from the scene
                ns = (False, False, False)
                return {(ns, self._obs_profile(ns)): 1.0}
            else:
                # Forklift stops; child remains, still in path, not moving
                ns = (True, False, False)
                return {(ns, self._obs_profile(ns)): 1.0}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, float]:
        return (0.0, 0.0)
