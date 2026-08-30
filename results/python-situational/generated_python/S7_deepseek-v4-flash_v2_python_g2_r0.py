from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# Provided abstract base class (not to be redefined)
class POSG(ABC):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple, float]:
        ...

    @abstractmethod
    def is_terminal(self, s) -> bool:
        ...

    @abstractmethod
    def legal_actions(self, s, i: int) -> Sequence:
        ...

    @abstractmethod
    def transition(self, s, a: Tuple) -> Mapping[Tuple, float]:
        ...

    @abstractmethod
    def rewards(self, s, a, s_next) -> Tuple[float, ...]:
        ...

    def action_profiles(self, s) -> Iterator[Tuple]:
        from itertools import product
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> Tuple:
        dist = self.initial_distribution()
        outcomes, probs = zip(*dist.items())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def sample_transition(self, s, a, rng: random.Random) -> Tuple:
        dist = self.transition(s, a)
        outcomes, probs = zip(*dist.items())
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def validate(self, states, tol=1e-09):
        for s in states:
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if len(acts) == 0:
                    raise ValueError(f"Empty actions for player {i} in state {s}")
        # Check initial distribution sums to 1
        init = self.initial_distribution()
        if abs(sum(init.values()) - 1.0) > tol:
            raise ValueError("Initial distribution does not sum to 1")
        # Check transitions
        for s in states:
            if self.is_terminal(s):
                continue
            for a in self.action_profiles(s):
                trans = self.transition(s, a)
                if abs(sum(trans.values()) - 1.0) > tol:
                    raise ValueError(f"Transition from {s} with {a} does not sum to 1")


class DeliveryDronePOSG(POSG):
    """Two players: drone (index 0) and dog (index 1).
    States: 'at_gate' (non-terminal), 'left' (terminal).
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple, float]:
        # (state, observation_profile)
        return {("at_gate", ("gate_locked_dog_barking", "drone_arrived")): 1.0}

    def is_terminal(self, s) -> bool:
        return s == "left"

    def legal_actions(self, s, i: int) -> Sequence:
        if s == "at_gate":
            if i == 0:  # drone
                return ("wait", "leave")
            else:       # dog
                return ("bark",)
        else:  # terminal state
            return ("noop",)

    def transition(self, s, a: Tuple) -> Mapping[Tuple, float]:
        if s == "at_gate":
            drone_action, dog_action = a
            if drone_action == "wait":
                return {("at_gate", ("dog_barking", "drone_present")): 1.0}
            else:  # leave
                return {("left", ("drone_left", "drone_gone")): 1.0}
        else:  # terminal self-loop
            return {(s, ("noop", "noop")): 1.0}

    def rewards(self, s, a, s_next) -> Tuple[float, ...]:
        return (0.0, 0.0)
