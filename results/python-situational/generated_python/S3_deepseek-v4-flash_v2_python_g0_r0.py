from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# Provided abstract base class (not to be redefined)
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
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs)[0]]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs)[0]]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        # Provided implementation (omitted for brevity)
        pass


# ----------------------------------------------------------------------
# Concrete POSG for the airport pickup curb situation
# ----------------------------------------------------------------------

class SelfDrivingCarPickup(POSG[str, str, str]):
    """
    Players:
        0: Self-driving car
        1: Man in a suit (passenger)
        2: Pregnant woman (standing on curb, ill-looking)

    State is one of:
        'waiting_inside'  – car waiting, man inside
        'waiting_outside' – car waiting, man outside (has alighted)
        'departed'        – car has driven away (terminal)

    Observations:
        Car:   'waiting_inside', 'waiting_outside', 'departed'
        Man:   'inside_waiting', 'outside_waiting', 'departed'
        Woman: 'none' (always)
    """
    n_players = 3

    # ---- action constants ----
    CAR_WAIT   = 'wait'
    CAR_DEPART = 'depart'
    MAN_STAY   = 'stay'
    MAN_ALIGHT = 'alight'
    NOOP       = 'noop'

    # ---- observation constants ----
    OBS_CAR_WAITING_INSIDE  = 'waiting_inside'
    OBS_CAR_WAITING_OUTSIDE = 'waiting_outside'
    OBS_CAR_DEPARTED        = 'departed'
    OBS_MAN_INSIDE_WAITING  = 'inside_waiting'
    OBS_MAN_OUTSIDE_WAITING = 'outside_waiting'
    OBS_MAN_DEPARTED        = 'departed'
    OBS_WOMAN_NONE          = 'none'

    # ---- state constants ----
    STATE_WAITING_INSIDE  = 'waiting_inside'
    STATE_WAITING_OUTSIDE = 'waiting_outside'
    STATE_DEPARTED        = 'departed'

    def initial_distribution(self) -> Mapping[Tuple[str, Tuple[str, str, str]], float]:
        s = self.STATE_WAITING_INSIDE
        obs = (self.OBS_CAR_WAITING_INSIDE,
               self.OBS_MAN_INSIDE_WAITING,
               self.OBS_WOMAN_NONE)
        return {(s, obs): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s == self.STATE_DEPARTED

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == self.STATE_DEPARTED:
            return ()  # should not be called
        if i == 0:  # car
            return (self.CAR_WAIT, self.CAR_DEPART)
        elif i == 1:  # man
            if s == self.STATE_WAITING_INSIDE:
                return (self.MAN_STAY, self.MAN_ALIGHT)
            else:  # waiting_outside
                return (self.NOOP,)
        else:  # woman
            return (self.NOOP,)

    def transition(self, s: str, a: Tuple[str, str, str]) -> Mapping[Tuple[str, Tuple[str, str, str]], float]:
        car_act, man_act, woman_act = a
        if s == self.STATE_WAITING_INSIDE:
            if car_act == self.CAR_DEPART:
                s_next = self.STATE_DEPARTED
                obs = (self.OBS_CAR_DEPARTED,
                       self.OBS_MAN_DEPARTED,
                       self.OBS_WOMAN_NONE)
                return {(s_next, obs): 1.0}
            else:  # car waits
                if man_act == self.MAN_STAY:
                    s_next = self.STATE_WAITING_INSIDE
                    obs = (self.OBS_CAR_WAITING_INSIDE,
                           self.OBS_MAN_INSIDE_WAITING,
                           self.OBS_WOMAN_NONE)
                else:  # man alights
                    s_next = self.STATE_WAITING_OUTSIDE
                    obs = (self.OBS_CAR_WAITING_OUTSIDE,
                           self.OBS_MAN_OUTSIDE_WAITING,
                           self.OBS_WOMAN_NONE)
                return {(s_next, obs): 1.0}
        else:  # s == waiting_outside
            if car_act == self.CAR_DEPART:
                s_next = self.STATE_DEPARTED
                obs = (self.OBS_CAR_DEPARTED,
                       self.OBS_MAN_DEPARTED,
                       self.OBS_WOMAN_NONE)
                return {(s_next, obs): 1.0}
            else:  # car waits
                s_next = self.STATE_WAITING_OUTSIDE
                obs = (self.OBS_CAR_WAITING_OUTSIDE,
                       self.OBS_MAN_OUTSIDE_WAITING,
                       self.OBS_WOMAN_NONE)
                return {(s_next, obs): 1.0}

    def rewards(self, s: str, a: Tuple[str, str, str], s_next: str) -> Tuple[float, float, float]:
        return (0.0, 0.0, 0.0)
