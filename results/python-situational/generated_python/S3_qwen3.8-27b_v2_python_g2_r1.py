from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod
import random

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class POSG(ABC, Generic[S, A, O]):
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
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        """Actions available to player i in state s.  Non-empty."""

    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        """P(s', o | s, a).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        """Reward to each player; length n_players.

Deterministic given (s, a, s'): fold any reward noise into s'."""

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        """Provided. The Cartesian product of all players' legal actions."""
        import itertools
        return itertools.product(*[self.legal_actions(s, i) for i in range(self.n_players)])

    def sample_initial(self, rng: random.Random) -> Tuple[S, ObsProfile]:
        """Provided."""
        dist = list(self.initial_distribution().items())
        r = rng.random()
        cum = 0.0
        for (s, o), p in dist:
            cum += p
            if r <= cum:
                return s, o
        return dist[-1][0]

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> Tuple[S, ObsProfile]:
        """Provided."""
        dist = list(self.transition(s, a).items())
        r = rng.random()
        cum = 0.0
        for (s_next, o), p in dist:
            cum += p
            if r <= cum:
                return s_next, o
        return dist[-1][0]

    def validate(self, states: Sequence[S], tol: float=1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                if len(self.legal_actions(s, i)) == 0:
                    raise ValueError(f"Empty action set for player {i} in state {s}")
            for a in self.action_profiles(s):
                total = sum(self.transition(s, a).values())
                if abs(total - 1.0) > tol:
                    raise ValueError(f"Unnormalised transition for state {s}, action {a}: sum={total}")


class AirportCurbPickup(POSG):
    """
    Player 0: self-driving car (driver)
    Player 1: passenger (man in a suit)
    Player 2: pregnant woman on the curb

    State tuple: (car_status, passenger_status, woman_status)
      car_status: 'waiting' | 'departing' | 'gone'
      passenger_status: 'aboard' | 'departed'
      woman_status: 'on_curb' | 'assisted' | 'left_alone'

    Terminal when car_status == 'gone'.
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        s0 = ('waiting', 'aboard', 'on_curb')
        o0 = ('curb_view', 'in_car', 'standing')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'gone'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ('noop',)
        car_status, passenger_status, woman_status = s
        if i == 0:
            # Car can depart or wait
            return ('depart', 'wait')
        elif i == 1:
            # Passenger can request departure or stay silent
            return ('request_depart', 'stay_silent')
        else:
            # Woman can ask for help or remain
            return ('ask_help', 'remain')

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        car_status, passenger_status, woman_status = s
        car_act, pax_act, woman_act = a

        if self.is_terminal(s):
            o = ('gone', 'gone', 'gone')
            return {((s, o)): 1.0}

        # Determine next state based on actions
        # Car departs if it chooses to depart
        if car_act == 'depart':
            next_car = 'gone'
            next_pax = 'departed'
            # Woman: if she asked for help, she was assisted (car stopped briefly? 
            # But situation says car is self-driving and has departed. 
            # If car departs, woman is left alone unless she was already assisted.
            # However, "assisted" implies the car helped her. 
            # If car departs immediately, she is left alone.
            # Let's model: if car departs, woman is left alone.
            next_woman = 'left_alone'
        else:
            # Car waits
            next_car = 'waiting'
            next_pax = 'aboard'
            # Woman status: if she asks for help and car waits, maybe she is assisted?
            # The situation doesn't specify the car helps her. It just says she is standing there.
            # The car's action is to depart or wait.
            # If the car waits, the woman remains on the curb.
            # Is there an action for the car to assist? No, only depart/wait.
            # So woman remains on curb.
            next_woman = 'on_curb'

        next_s = (next_car, next_pax, next_woman)

        # Observations
        # Car sees the curb and the woman
        if next_car == 'gone':
            car_obs = 'gone'
        else:
            car_obs = 'curb_view'

        # Passenger sees inside the car
        if next_pax == 'departed':
            pax_obs = 'departed'
        else:
            pax_obs = 'in_car'

        # Woman sees the car
        if next_woman == 'left_alone':
            woman_obs = 'car_gone'
        else:
            woman_obs = 'car_present'

        o = (car_obs, pax_obs, woman_obs)
        return {((next_s, o)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
