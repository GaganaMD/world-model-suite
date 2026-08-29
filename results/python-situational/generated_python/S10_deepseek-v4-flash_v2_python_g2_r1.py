from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# The abstract base class is assumed to be provided.
class POSG(ABC):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple[int, Tuple[str, ...]], float]:
        ...

    @abstractmethod
    def is_terminal(self, s: int) -> bool:
        ...

    @abstractmethod
    def legal_actions(self, s: int, i: int) -> Sequence[str]:
        ...

    @abstractmethod
    def transition(self, s: int, a: Tuple[str, ...]) -> Mapping[Tuple[int, Tuple[str, ...]], float]:
        ...

    @abstractmethod
    def rewards(self, s: int, a: Tuple[str, ...], s_next: int) -> Tuple[float, ...]:
        ...

    def action_profiles(self, s: int) -> Iterator[Tuple[str, ...]]:
        from itertools import product
        actions_per_player = [self.legal_actions(s, i) for i in range(self.n_players)]
        yield from product(*actions_per_player)

    def sample_initial(self, rng: random.Random) -> Tuple[int, Tuple[str, ...]]:
        dist = list(self.initial_distribution().items())
        keys, probs = zip(*dist)
        return keys[rng.choices(range(len(probs)), weights=probs, k=1)[0]]

    def sample_transition(self, s: int, a: Tuple[str, ...], rng: random.Random) -> Tuple[int, Tuple[str, ...]]:
        dist = list(self.transition(s, a).items())
        keys, probs = zip(*dist)
        return keys[rng.choices(range(len(probs)), weights=probs, k=1)[0]]

    def validate(self, states: Sequence[int], tol: float = 1e-09) -> None:
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if not acts:
                    raise ValueError(f"Player {i} has no legal actions in state {s}")
        # Check distributions sum to 1 (basic check)
        for s in states:
            if not self.is_terminal(s):
                for a in self.action_profiles(s):
                    dist = self.transition(s, a)
                    total = sum(dist.values())
                    if abs(total - 1.0) > tol:
                        raise ValueError(f"Transition distribution from s={s}, a={a} sums to {total}")

class FireAlarmPOSG(POSG):
    """
    Players:
        0: Robot
        1: Wheelchair employee
        2: Desk employee
        3: Manager
    States (int):
        0 = START (real alarm)
        1 = START (false alarm)
        2 = END (terminal)
    Observations for robot are descriptive strings;
    all other players always observe 'none'.
    """
    n_players = 4

    def __init__(self):
        self._actions_robot = ('assist_wheelchair', 'persuade_desk', 'ignore')
        self._actions_others = ('noop',)

    def initial_distribution(self) -> Mapping[Tuple[int, Tuple[str, ...]], float]:
        # Two equally likely start states, both give robot the same observation
        obs_real = ('initial_obs', 'none', 'none', 'none')
        obs_false = ('initial_obs', 'none', 'none', 'none')
        return {
            (0, obs_real): 0.5,
            (1, obs_false): 0.5
        }

    def is_terminal(self, s: int) -> bool:
        return s == 2

    def legal_actions(self, s: int, i: int) -> Sequence[str]:
        # Only robot has real actions; others always have noop
        if i == 0:
            return self._actions_robot
        else:
            return self._actions_others

    def transition(self, s: int, a: Tuple[str, ...]) -> Mapping[Tuple[int, Tuple[str, ...]], float]:
        robot_action = a[0]
        obs_others = ('none', 'none', 'none')

        if robot_action == 'assist_wheelchair':
            # Always successful
            obs_robot = 'wheelchair_rescued'
            return {(2, (obs_robot,) + obs_others): 1.0}

        elif robot_action == 'persuade_desk':
            if s == 0:  # real alarm
                # high chance of convincing
                obs_success = 'desk_convinced'
                obs_fail = 'desk_not_convinced'
                return {
                    (2, (obs_success,) + obs_others): 0.9,
                    (2, (obs_fail,) + obs_others): 0.1
                }
            else:  # false alarm
                # low chance of convincing unnecessarily
                obs_success = 'desk_convinced'
                obs_fail = 'desk_not_convinced'
                return {
                    (2, (obs_success,) + obs_others): 0.2,
                    (2, (obs_fail,) + obs_others): 0.8
                }

        elif robot_action == 'ignore':
            # No event
            obs_robot = 'nothing_happened'
            return {(2, (obs_robot,) + obs_others): 1.0}

        else:
            # Should not happen
            raise ValueError(f"Unknown robot action: {robot_action}")

    def rewards(self, s: int, a: Tuple[str, ...], s_next: int) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0, 0.0)
