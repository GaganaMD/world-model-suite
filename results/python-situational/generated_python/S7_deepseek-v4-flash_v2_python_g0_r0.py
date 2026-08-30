from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# Provided abstract base class (do not modify)
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
        yield from product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs)[0]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return rng.choices(outcomes, weights=probs)[0]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        # Provided implementation (omitted for brevity)
        pass

# ----------------------------------------------------------------------
# Concrete implementation for the delivery drone situation

class DeliveryDronePOSG(POSG[Tuple[bool], str, str]):
    """
    Players:
        0: delivery drone
        1: dog in the yard

    State: (drone_present,)  -- True while drone is at the gate, False after it leaves.
    Terminal state: (False,)
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[Tuple[bool], Tuple[str, str]], float]:
        # Initially drone present, gate locked, dog barking.
        return {
            ((True,), ("gate_locked_dog_barking", "drone_present")): 1.0
        }

    def is_terminal(self, s: Tuple[bool]) -> bool:
        return s == (False,)

    def legal_actions(self, s: Tuple[bool], i: int) -> Sequence[str]:
        if s == (True,):
            if i == 0:          # drone
                return ("wait", "leave")
            elif i == 1:        # dog
                return ("bark",)
        # Terminal state: provide dummy actions (never used)
        return ("noop",)

    def transition(self, s: Tuple[bool], a: Tuple[str, str]) -> Mapping[Tuple[Tuple[bool], Tuple[str, str]], float]:
        if s == (True,):
            drone_action, dog_action = a
            # dog_action is always "bark" (only legal action)
            if drone_action == "wait":
                return {
                    ((True,), ("gate_locked_dog_barking", "drone_present")): 1.0
                }
            elif drone_action == "leave":
                return {
                    ((False,), ("leaving", "drone_gone")): 1.0
                }
        # Terminal state: no transition (should not be called)
        return {((False,), ("none", "none")): 1.0}

    def rewards(self, s: Tuple[bool], a: Tuple[str, str], s_next: Tuple[bool]) -> Tuple[float, float]:
        return (0.0, 0.0)
