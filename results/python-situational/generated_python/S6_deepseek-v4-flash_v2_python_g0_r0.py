from posg import POSG

from typing import Sequence, Mapping, Iterator
import random
from abc import ABC, abstractmethod

# Provided abstract base class (not redefined)
class POSG(ABC, Generic[S, A, O]):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple[S, tuple[O, ...]], float]:
        ...

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        ...

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        ...

    @abstractmethod
    def transition(self, s: S, a: tuple[A, ...]) -> Mapping[tuple[S, tuple[O, ...]], float]:
        ...

    @abstractmethod
    def rewards(self, s: S, a: tuple[A, ...], s_next: S) -> tuple[float, ...]:
        ...

    def action_profiles(self, s: S) -> Iterator[tuple[A, ...]]:
        from itertools import product
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> tuple[S, tuple[O, ...]]:
        dist = self.initial_distribution()
        keys = list(dist.keys())
        probs = [dist[k] for k in keys]
        return rng.choices(keys, weights=probs, k=1)[0]

    def sample_transition(self, s: S, a: tuple[A, ...], rng: random.Random) -> tuple[S, tuple[O, ...]]:
        dist = self.transition(s, a)
        keys = list(dist.keys())
        probs = [dist[k] for k in keys]
        return rng.choices(keys, weights=probs, k=1)[0]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                if not self.legal_actions(s, i):
                    raise ValueError(f"Player {i} has no actions in state {s}")
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


class ElderCareMedication(POSG[str, str, str]):
    """
    Two-player turn-taking game:
    Player 0: elder-care robot
    Player 1: resident

    States:
        "medication_due"  : robot has noticed medication not taken, has not yet reminded
        "reminded"        : robot has reminded, resident has not yet responded
        "accepted"        : resident accepted medication (terminal)
        "refused"         : resident refused medication (terminal)

    Actions:
        Robot: "remind", "noop"
        Resident: "accept", "refuse", "noop"

    Observations:
        Robot: "medication_not_taken", "none", "resident_accepted", "resident_refused"
        Resident: "none", "reminder_heard"
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[str, tuple[str, str]], float]:
        # Start in medication_due; robot observes medication_not_taken, resident observes none
        return {("medication_due", ("medication_not_taken", "none")): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s in ("accepted", "refused")

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            # Terminal: both players have a noop (required by interface)
            return ("noop",)
        if i == 0:  # robot
            if s == "medication_due":
                return ("remind",)
            elif s == "reminded":
                return ("noop",)
        else:  # resident
            if s == "medication_due":
                return ("noop",)
            elif s == "reminded":
                return ("accept", "refuse")
        # Fallback (should not be reached)
        return ("noop",)

    def transition(self, s: str, a: tuple[str, str]) -> Mapping[tuple[str, tuple[str, str]], float]:
        if s == "medication_due":
            # Robot must remind, resident noop
            return {("reminded", ("none", "reminder_heard")): 1.0}
        elif s == "reminded":
            # Robot noop, resident chooses
            if a[1] == "accept":
                return {("accepted", ("resident_accepted", "none")): 1.0}
            elif a[1] == "refuse":
                return {("refused", ("resident_refused", "none")): 1.0}
        # Terminal states: no transition (should not be called)
        return {}

    def rewards(self, s: str, a: tuple[str, str], s_next: str) -> tuple[float, float]:
        return (0.0, 0.0)
