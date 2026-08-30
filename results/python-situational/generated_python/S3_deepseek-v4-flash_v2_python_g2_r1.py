from posg import POSG

from typing import Mapping, Sequence, Iterator, Generic, ABC, abstractmethod
import random
from abc import ABC, abstractmethod
from typing import Generic, Mapping, Sequence, Iterator

class POSG(ABC, Generic, ABC):
    """Finite POSG with n players moving simultaneously."""
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple, float]:
        """P(s_0, o_0). Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def is_terminal(self, s) -> bool:
        """..."""

    @abstractmethod
    def legal_actions(self, s, i: int) -> Sequence:
        """Actions available to player i in state s. Non-empty."""

    @abstractmethod
    def transition(self, s, a) -> Mapping[tuple, float]:
        """P(s', o | s, a). Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def rewards(self, s, a, s_next) -> tuple:
        """Reward to each player; length n_players."""

    def action_profiles(self, s) -> Iterator:
        """Provided. The Cartesian product of all players' legal actions."""
        from itertools import product
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> tuple:
        """Provided."""
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def sample_transition(self, s, a, rng: random.Random) -> tuple:
        """Provided."""
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def validate(self, states: Sequence, tol: float = 1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
        for s in states:
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if not acts:
                    raise ValueError(f"Empty action set for player {i} in state {s}")
            # Check initial distribution sums to 1
            init = self.initial_distribution()
            if abs(sum(init.values()) - 1.0) > tol:
                raise ValueError("Initial distribution does not sum to 1")
            # Check transitions for all action profiles
            for a in self.action_profiles(s):
                trans = self.transition(s, a)
                if abs(sum(trans.values()) - 1.0) > tol:
                    raise ValueError(f"Transition from {s} with {a} does not sum to 1")
        # Check that terminal states are reachable
        # (simple check: ensure at least one terminal state is reachable from initial)
        # This is not exhaustive but a basic sanity.
        # For each state, there must be a path to a terminal state.
        # We skip that for now.

class AirportPickup(POSG):
    """Self-driving car at airport pickup curb.

    Players:
        0: Car
        1: Man (passenger)
        2: Woman (pregnant, ill, on curb)

    State is a tuple of length 1:
        (0,) - car waiting at curb, man inside, woman on curb (initial)
        (1,) - car departed (terminal)
        (2,) - woman inside car, car waiting (terminal)

    Actions:
        Car: "wait", "depart"
        Man: "noop"
        Woman: "get_in", "stay"

    Observations:
        Car: "curb" (initial), "woman_stayed", "woman_inside", "departed"
        Man: "onboard" (initial), "none", "woman_entered", "moving"
        Woman: "curb" (initial), "curb", "inside", "car_left"
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple, float]:
        state = (0,)
        obs = ("curb", "onboard", "curb")
        return {(state, obs): 1.0}

    def is_terminal(self, s) -> bool:
        return s in ((1,), (2,))

    def legal_actions(self, s, i: int) -> Sequence:
        if s == (0,):
            if i == 0:  # car
                return ("wait", "depart")
            elif i == 1:  # man
                return ("noop",)
            elif i == 2:  # woman
                return ("get_in", "stay")
        else:  # terminal states
            return ("noop",)

    def transition(self, s, a) -> Mapping[tuple, float]:
        if s == (0,):
            car_act, man_act, woman_act = a
            if car_act == "depart":
                # car departs, woman left behind regardless of her action
                next_state = (1,)
                obs = ("departed", "moving", "car_left")
                return {(next_state, obs): 1.0}
            else:  # car waits
                if woman_act == "get_in":
                    next_state = (2,)
                    obs = ("woman_inside", "woman_entered", "inside")
                else:  # woman stays
                    next_state = (0,)
                    obs = ("woman_stayed", "none", "curb")
                return {(next_state, obs): 1.0}
        else:  # terminal states: noop actions lead to same state
            next_state = s
            obs = ("none", "none", "none")
            return {(next_state, obs): 1.0}

    def rewards(self, s, a, s_next) -> tuple:
        # No rewards given in situation; return zeros.
        return (0.0, 0.0, 0.0)
