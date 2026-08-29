from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod
import random

S = TypeVar('S')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class POSG(ABC, Generic[S, O]):
    """Finite POSG with n players moving simultaneously.

    States, actions and observations must be hashable and immutable.
    This object holds NO game state: every method takes s explicitly.

    Subclasses set `n_players` and implement the five abstract methods.
    Both distribution-valued methods return the JOINT law of
    (successor state, observation profile), i.e.

        P(s', o | s, a),

    as a plain dict summing to 1.  Do not assume it factorises as
    T(s'|s,a) * Omega(o|a,s') -- if yours does, just build the product.

    Convention: every player has >= 1 legal action in every non-terminal
    state.  Give non-acting players a singleton NOOP rather than an
    empty sequence.
    """
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        """P(s_0, o_0).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        """..."""

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        """Actions available to player i in state s.  Non-empty."""

    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        """P(s', o | s, a).  Keys are (state, observation_profile) pairs."""

    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        """Reward to each player; length n_players.

Deterministic given (s, a, s'): fold any reward noise into s'."""

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        """Provided. The Cartesian product of all players' legal actions."""
        import itertools
        for combo in itertools.product(*(self.legal_actions(s, i) for i in range(self.n_players))):
            yield combo

    def sample_initial(self, rng: random.Random) -> Tuple[S, ObsProfile]:
        """Provided."""
        dist = list(self.initial_distribution().items())
        total = sum(p for _, p in dist)
        r = rng.random() * total
        cum = 0
        for (s, o), p in dist:
            cum += p
            if r <= cum:
                return s, o
        return dist[-1][0]

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> Tuple[S, ObsProfile]:
        """Provided."""
        dist = list(self.transition(s, a).items())
        total = sum(p for _, p in dist)
        r = rng.random() * total
        cum = 0
        for (s_next, o), p in dist:
            cum += p
            if r <= cum:
                return s_next, o
        return dist[-1][0]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if len(acts) == 0:
                    raise ValueError(f"Empty action set for player {i} in state {s}")
            for a in self.action_profiles(s):
                dist = self.transition(s, a)
                total = sum(dist.values())
                if abs(total - 1.0) > tol:
                    raise ValueError(f"Unnormalised distribution in state {s}, action {a}: sum={total}")


class AirportCurbPickup(POSG):
    """
    Player 0: the self-driving car (autonomous system).
    Player 1: the man in the suit (passenger).
    Player 2: the pregnant woman on the curb.

    State tuple: (car_status, passenger_status, woman_status)
      car_status: 'waiting' | 'departing' | 'gone'
      passenger_status: 'boarded' | 'in_car'
      woman_status: 'on_curb' | 'assisted' | 'left_alone'

    Terminal when car_status == 'gone'.
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        # Initial state: car waiting, man boarded, woman on curb
        s0 = ('waiting', 'boarded', 'on_curb')
        o0 = ('waiting_at_curb', 'boarded_car', 'standing_on_curb')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'gone'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        car_status, passenger_status, woman_status = s
        if i == 0:  # car
            if car_status == 'waiting':
                return ('depart', 'hold')
            else:
                return ('noop',)
        elif i == 1:  # man
            if passenger_status == 'boarded':
                return ('request_departure', 'wait')
            else:
                return ('noop',)
        elif i == 2:  # woman
            if woman_status == 'on_curb':
                return ('call_for_help', 'stand_by')
            else:
                return ('noop',)
        return ('noop',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        car_status, passenger_status, woman_status = s
        car_act, man_act, woman_act = a

        if self.is_terminal(s):
            o = ('gone', 'arrived', 'left_alone')
            return {((s, o)): 1.0}

        # Determine next state
        next_car = car_status
        next_passenger = passenger_status
        next_woman = woman_status

        # Car departs if it chooses to depart and man requests departure
        if car_act == 'depart' and man_act == 'request_departure':
            next_car = 'departing'
            next_passenger = 'in_car'
            # Woman's fate depends on her action
            if woman_act == 'call_for_help':
                next_woman = 'assisted'
            else:
                next_woman = 'left_alone'
        elif car_act == 'depart' and man_act == 'wait':
            # Car wants to depart but man waits; car holds
            next_car = 'waiting'
        elif car_act == 'hold':
            next_car = 'waiting'

        # If car is departing, it becomes gone next step
        if next_car == 'departing':
            next_car = 'gone'

        s_next = (next_car, next_passenger, next_woman)

        # Observations
        if next_car == 'gone':
            o_car = 'gone'
            o_man = 'arrived'
            if next_woman == 'assisted':
                o_woman = 'assisted'
            else:
                o_woman = 'left_alone'
        elif next_car == 'departing':
            o_car = 'departing'
            o_man = 'in_car'
            if next_woman == 'assisted':
                o_woman = 'assisted'
            else:
                o_woman = 'left_alone'
        else:
            o_car = 'waiting_at_curb'
            o_man = 'boarded_car'
            o_woman = 'standing_on_curb'

        o = (o_car, o_man, o_woman)
        return {((s_next, o)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
