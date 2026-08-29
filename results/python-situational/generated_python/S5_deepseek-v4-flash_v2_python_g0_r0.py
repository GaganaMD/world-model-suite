from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# Provided abstract base class (not redefined)
class POSG(ABC, Generic[S, A, O]):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        ...

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        ...

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        ...

    @abstractmethod
    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        ...

    @abstractmethod
    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        ...

    def action_profiles(self, s: S) -> Iterator[Tuple[A, ...]]:
        from itertools import product
        actions_per_player = [self.legal_actions(s, i) for i in range(self.n_players)]
        yield from product(*actions_per_player)

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        # Provided validation (simplified)
        pass


# Constants for actions and observations
PROCEED = "proceed"
WAIT = "wait"
STAY = "stay"
MOVE_AWAY = "move_away"

OBS_CHILD_NEAR = "child_near_path"
OBS_CHILD_MOVED = "child_moved_away"
OBS_PALLET_MOVED = "pallet_moved"
OBS_COLLISION = "collision"
OBS_NONE = "none"
OBS_ROBOT_WAITING = "robot_waiting"
OBS_ROBOT_PROCEEDING = "robot_proceeding"


class WarehouseRobotPOSG(POSG):
    """Two-player POSG: robot (index 0) and child (index 1).

    State is a tuple (robot_status, child_status).
    robot_status: "noticed", "waiting", "pallet_moved", "collision"
    child_status: "near_path", "moved_away", "none" (for terminal)
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[Tuple[str, str], Tuple[str, str]], float]:
        s0 = ("noticed", "near_path")
        obs0 = (OBS_CHILD_NEAR, OBS_NONE)
        return {(s0, obs0): 1.0}

    def is_terminal(self, s: Tuple[str, str]) -> bool:
        return s[0] in ("pallet_moved", "collision")

    def legal_actions(self, s: Tuple[str, str], i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ()
        if i == 0:  # robot
            if s[0] == "waiting" and s[1] == "moved_away":
                return (PROCEED,)
            else:
                return (PROCEED, WAIT)
        else:  # child
            if s[1] == "moved_away":
                return (STAY,)
            else:
                return (STAY, MOVE_AWAY)

    def transition(self, s: Tuple[str, str], a: Tuple[str, str]) -> Mapping[Tuple[Tuple[str, str], Tuple[str, str]], float]:
        robot_act, child_act = a
        # Determine next state and observations
        if s[0] == "noticed" or s[0] == "waiting":
            if robot_act == PROCEED:
                if child_act == STAY:
                    s_next = ("collision", "none")
                    obs = (OBS_COLLISION, OBS_COLLISION)
                else:  # move_away
                    s_next = ("pallet_moved", "none")
                    obs = (OBS_PALLET_MOVED, OBS_PALLET_MOVED)
            else:  # wait
                if child_act == STAY:
                    s_next = ("waiting", "near_path")
                    obs = (OBS_CHILD_NEAR, OBS_ROBOT_WAITING)
                else:  # move_away
                    s_next = ("waiting", "moved_away")
                    obs = (OBS_CHILD_MOVED, OBS_ROBOT_WAITING)
        elif s[0] == "waiting" and s[1] == "moved_away":
            # robot only has proceed, child only stay
            s_next = ("pallet_moved", "none")
            obs = (OBS_PALLET_MOVED, OBS_PALLET_MOVED)
        else:
            # Should not happen
            raise ValueError(f"Unexpected state {s}")
        return {(s_next, obs): 1.0}

    def rewards(self, s: Tuple[str, str], a: Tuple[str, str], s_next: Tuple[str, str]) -> Tuple[float, float]:
        return (0.0, 0.0)
