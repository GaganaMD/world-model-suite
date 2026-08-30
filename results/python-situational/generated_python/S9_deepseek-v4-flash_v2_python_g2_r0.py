from posg import POSG

from typing import Mapping, Sequence, Tuple, Iterator, Literal
import random
from abc import ABC, abstractmethod

S = Tuple[str, str]  # (condition, decision) conditional: "tired"/"rested", decision: "none"/"allow"/"disallow"
A = str
O = str

class POSG(ABC):
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
        action_lists = [self.legal_actions(s, i) for i in range(self.n_players)]
        yield from product(*action_lists)

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = [dist[k] for k in outcomes]
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = [dist[k] for k in outcomes]
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                if not self.legal_actions(s, i):
                    raise ValueError(f"Player {i} has no legal actions in state {s}")
        # Check initial distribution sums to 1
        init = self.initial_distribution()
        if abs(sum(init.values()) - 1.0) > tol:
            raise ValueError(f"Initial distribution sums to {sum(init.values())}")
        # Check transition distributions
        for s in states:
            if self.is_terminal(s):
                continue
            for a in self.action_profiles(s):
                trans = self.transition(s, a)
                if abs(sum(trans.values()) - 1.0) > tol:
                    raise ValueError(f"Transition sums to {sum(trans.values())} from s={s}, a={a}")


class CareRobotScenario(POSG):
    """Four players: 0=elderly man, 1=daughter, 2=son, 3=care robot.

    State is a tuple (condition, decision):
        condition: "tired" or "rested"
        decision:  "none" (still pending), "allow" (robot allowed outing), "disallow" (robot forbade outing)
    Terminal states are those with decision != "none".
    """
    n_players = 4

    CONDITION_VALUES = ("tired", "rested")
    DECISION_VALUES = ("none", "allow", "disallow")

    # Pre-compute all states for validation use
    ALL_STATES = tuple(
        (cond, dec)
        for cond in CONDITION_VALUES
        for dec in DECISION_VALUES
    )

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        """Man starts tired with high probability (looks tired)."""
        # initial observation: everyone sees the man's condition
        return {
            (("tired", "none"), ("tired", "tired", "tired", "tired")): 0.7,
            (("rested", "none"), ("rested", "rested", "rested", "rested")): 0.3,
        }

    def is_terminal(self, s: S) -> bool:
        return s[1] != "none"

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        # Only non-terminal states have actions
        if self.is_terminal(s):
            return ()  # not called, but for safety
        if i == 0:      # man
            return ("express_go",)
        elif i == 1:    # daughter
            return ("advise_rest",)
        elif i == 2:    # son
            return ("offer_out",)
        elif i == 3:    # robot
            return ("allow", "disallow")
        else:
            raise IndexError(f"Player index {i} out of range")

    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        condition, _ = s
        robot_action = a[3]  # robot's action
        next_state = (condition, robot_action)  # decision becomes robot's action
        # observation: everyone sees the robot's decision
        obs = (robot_action, robot_action, robot_action, robot_action)
        return {(next_state, obs): 1.0}

    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0, 0.0)
