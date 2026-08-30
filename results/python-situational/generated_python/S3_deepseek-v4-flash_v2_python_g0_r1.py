from posg import POSG

from typing import Generic, Mapping, Sequence, Iterator, Tuple
import random
from abc import ABC, abstractmethod

# Provided abstract base class (assumed already imported, but we include for completeness)
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
        actions = [self.legal_actions(s, i) for i in range(self.n_players)]
        yield from product(*actions)

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs, k=1)[0]]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs, k=1)[0]]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        # Provided implementation (omitted for brevity)
        pass


# Module-level constants
CAR_ACTIONS = ('depart', 'wait')
MAN_ACTIONS = ('say_go', 'say_stay', 'noop')
WOMAN_ACTIONS = ('signal', 'noop')

INITIAL_OBS = ('woman_ill', 'inside', 'on_curb')
TERMINAL_OBS = ('none', 'none', 'none')


class AirportPickupPOSG(POSG[str, str, str]):
    """
    Players:
        0: self-driving car
        1: man in a suit (passenger, inside the car)
        2: pregnant woman (pedestrian, standing on the curb)

    States:
        'waiting'  – car is at the curb, man inside, woman on curb
        'departed' – car has driven away (terminal)
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        return {('waiting', INITIAL_OBS): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s == 'departed'

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == 'departed':
            return ('none',)  # not used, but required for interface
        if i == 0:
            return CAR_ACTIONS
        elif i == 1:
            return MAN_ACTIONS
        else:  # i == 2
            return WOMAN_ACTIONS

    def transition(self, s: str, a: Tuple[str, ...]) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        car_action, man_action, woman_action = a
        if car_action == 'depart':
            return {('departed', TERMINAL_OBS): 1.0}
        else:  # car waits
            car_obs = (man_action, woman_action)   # car sees both
            man_obs = woman_action                 # man sees woman's action
            woman_obs = (car_action, man_action)   # woman sees car and hears man
            obs_profile = (car_obs, man_obs, woman_obs)
            return {('waiting', obs_profile): 1.0}

    def rewards(self, s: str, a: Tuple[str, ...], s_next: str) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
