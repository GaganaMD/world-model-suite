from posg import POSG

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Mapping, Sequence, Iterator, tuple as Tuple
import random

S = TypeVar("S")
A = TypeVar("A")
O = TypeVar("O")

class POSG(ABC, Generic[S, A, O]):
    """Finite POSG with n players moving simultaneously."""
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple[S, Tuple[O, ...]], float]:
        pass

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        pass

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        pass

    @abstractmethod
    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[tuple[S, Tuple[O, ...]], float]:
        pass

    @abstractmethod
    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        pass

    def action_profiles(self, s: S) -> Iterator[Tuple[A, ...]]:
        from itertools import product
        profiles = [self.legal_actions(s, i) for i in range(self.n_players)]
        return (tuple(p) for p in product(*profiles))

    def sample_initial(self, rng: random.Random) -> tuple[S, Tuple[O, ...]]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                if not self.legal_actions(s, i):
                    raise ValueError(f"empty action set for player {i} in {s}")
            for a in self.action_profiles(s):
                d = self.transition(s, a)
                if abs(sum(d.values()) - 1.0) > tol:
                    raise ValueError(f"transition not normalized for {s}, {a}")


class SelfDrivingCarPickupPOSG(POSG):
    """A self-driving car is at an airport pickup curb.

    Player 0 is the self-driving car.
    Player 1 is the man in a suit who has boarded.
    Player 2 is the pregnant woman standing beside the car.

    State tuple meaning:
      (car_place, passenger_status, bystander_status)
      car_place: whether the car is at the curb
      passenger_status: whether the man remains inside
      bystander_status: whether the woman remains beside the car
    """

    n_players = 3

    def initial_distribution(self):
        # The car is waiting at the curb, the man has just boarded,
        # and the woman is standing next to the car.
        s = ("waiting_at_curb", "man_on_board", "woman_on_curb")
        o = ("none", "none", "none")
        return {(s, (o, o, o)): 1.0}

    def is_terminal(self, s):
        return s[0] == "departed"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            # Convention: non-terminal only; return a harmless singleton.
            return ("noop",)

        if i == 0:
            if s[0] == "waiting_at_curb":
                return ("wait", "depart")
            return ("noop",)

        # The man and woman are not described as acting after the initial moment.
        return ("noop",)

    def transition(self, s, a):
        car_action = a[0]

        if self.is_terminal(s):
            return {(s, ("none", "none", "none")): 1.0}

        if car_action == "depart":
            s_next = ("departed", "man_on_board", "woman_on_curb")
            obs = ("departing", "none", "none")
            return {(s_next, obs): 1.0}

        # car_action == "wait"
        obs = ("waiting", "none", "none")
        return {(s, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
