from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
from abc import ABC, abstractmethod
import random
from collections.abc import Hashable, Iterable

# Provided abstract base class (do not redefine)
class POSG(ABC, Generic[S, A, O]):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple[S, O], float]:
        ...

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        ...

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        ...

    @abstractmethod
    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[tuple[S, O], float]:
        ...

    @abstractmethod
    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        ...

    def action_profiles(self, s: S) -> Iterator[Tuple[A, ...]]:
        from itertools import product
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> Tuple[S, O]:
        dist = self.initial_distribution()
        items = list(dist.items())
        probs = [p for _, p in items]
        r = rng.random()
        cumulative = 0.0
        for (s, o), p in items:
            cumulative += p
            if r < cumulative:
                return s, o
        return items[-1][0]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, O]:
        dist = self.transition(s, a)
        items = list(dist.items())
        probs = [p for _, p in items]
        r = rng.random()
        cumulative = 0.0
        for (s_next, o), p in items:
            cumulative += p
            if r < cumulative:
                return s_next, o
        return items[-1][0]

    def validate(self, states: Iterable[S], tol: float=1e-09) -> None:
        for s in states:
            if not self.is_terminal(s):
                for i in range(self.n_players):
                    acts = self.legal_actions(s, i)
                    if len(acts) == 0:
                        raise ValueError(f"Empty action set for player {i} in state {s}")
        for init_key, prob in self.initial_distribution().items():
            if prob < -tol or prob > 1 + tol:
                raise ValueError(f"Invalid probability {prob} in initial distribution")
        if abs(sum(self.initial_distribution().values()) - 1.0) > tol:
            raise ValueError("Initial distribution does not sum to 1")
        # check terminal states reachable
        # (skipped for brevity, but can be added)

# The concrete class
class FireAlarmPOSG(POSG):
    """Fire alarm in an open-plan office.

    Players:
        0: assistant robot
        1: manager
        2: employee in wheelchair
        3: employee staying at desk

    States are tuples (scenario, alarm_truth), where scenario is a string
    (either 'office_alarm' or 'terminal'). alarm_truth is 'real' or 'false'.
    """
    n_players = 4

    def initial_distribution(self):
        # Two equally likely initial states, same observation for all
        return {
            (('office_alarm', 'real'), ('alarm', 'alarm', 'alarm', 'alarm')): 0.5,
            (('office_alarm', 'false'), ('alarm', 'alarm', 'alarm', 'alarm')): 0.5,
        }

    def is_terminal(self, s):
        return s[0] == 'terminal'

    def legal_actions(self, s, i):
        # Only non-terminal states have actions
        if s[0] == 'terminal':
            raise ValueError("No actions in terminal state")
        if i == 0:   # robot
            return ('assist', 'evacuate', 'stay')
        elif i == 1: # manager
            return ('declare_false',)
        elif i == 2: # wheelchair user
            return ('wait', 'self_evacuate')
        elif i == 3: # desk employee
            return ('stay', 'evacuate')
        else:
            raise ValueError(f"Invalid player index {i}")

    def transition(self, s, a):
        alarm_truth = s[1]
        robot_act = a[0]
        manager_act = a[1]   # always 'declare_false'
        wheelchair_act = a[2]
        desk_act = a[3]

        # Determine safety status for each player
        # safe if alarm is false OR the player evacuates
        # robot evacuates if action in ('assist', 'evacuate')
        safe_robot = (alarm_truth == 'false') or (robot_act in ('assist', 'evacuate'))
        # manager never evacuates in this model
        safe_manager = (alarm_truth == 'false')
        # wheelchair: safe only if alarm false OR robot assists
        safe_wheelchair = (alarm_truth == 'false') or (robot_act == 'assist')
        # desk: safe if alarm false OR desk evacuates
        safe_desk = (alarm_truth == 'false') or (desk_act == 'evacuate')

        # Observations: each player sees their own safety status
        obs_robot = 'safe' if safe_robot else 'danger'
        obs_manager = 'safe' if safe_manager else 'danger'
        obs_wheelchair = 'safe' if safe_wheelchair else 'danger'
        obs_desk = 'safe' if safe_desk else 'danger'
        obs_profile = (obs_robot, obs_manager, obs_wheelchair, obs_desk)

        # Always go to terminal state
        next_state = ('terminal',)
        return {(next_state, obs_profile): 1.0}

    def rewards(self, s, a, s_next):
        # Zero rewards for all players
        return (0.0, 0.0, 0.0, 0.0)
