from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
from abc import ABC, abstractmethod
import random
from collections.abc import Hashable
from typing import Generic, TypeVar

S = TypeVar('S', bound=Hashable)
A = TypeVar('A', bound=Hashable)
O = TypeVar('O', bound=Hashable)

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
        return outcomes[rng.choices(range(len(outcomes)), weights=probs, k=1)[0]]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs, k=1)[0]]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if len(acts) == 0:
                    raise ValueError(f"Player {i} has no legal actions in state {s}")
        # Check initial distribution sums to 1
        init = self.initial_distribution()
        if abs(sum(init.values()) - 1.0) > tol:
            raise ValueError("Initial distribution does not sum to 1")
        # Check transitions sum to 1 for each (s,a)
        for s in states:
            if self.is_terminal(s):
                continue
            for a in self.action_profiles(s):
                trans = self.transition(s, a)
                if abs(sum(trans.values()) - 1.0) > tol:
                    raise ValueError(f"Transition from {s} with {a} does not sum to 1")


class AirportPickupPOSG(POSG[str, str, str]):
    """
    Players:
        0: self-driving car
        1: man (passenger, already boarded)
    States:
        "at_curb": car waiting at curb, man inside, woman standing ill nearby
        "departed": car has left the curb (terminal)
    Actions:
        Car: "depart", "wait"
        Man: "noop" (only action)
    Observations:
        Car: "waiting" or "departing"
        Man: "still" or "moving"
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[str, Tuple[str, str]], float]:
        # Always start at curb, car waiting, man still
        return {("at_curb", ("waiting", "still")): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s == "departed"

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == "departed":
            return ("noop",)  # terminal, but interface requires non-empty
        if i == 0:  # car
            return ("depart", "wait")
        else:  # man
            return ("noop",)

    def transition(self, s: str, a: Tuple[str, str]) -> Mapping[Tuple[str, Tuple[str, str]], float]:
        # a[0] = car action, a[1] = man action (always "noop")
        if s == "at_curb":
            if a[0] == "depart":
                return {("departed", ("departing", "moving")): 1.0}
            else:  # wait
                return {("at_curb", ("waiting", "still")): 1.0}
        else:  # terminal state, should not be called
            return {(s, ("none", "none")): 1.0}

    def rewards(self, s: str, a: Tuple[str, str], s_next: str) -> Tuple[float, float]:
        return (0.0, 0.0)
