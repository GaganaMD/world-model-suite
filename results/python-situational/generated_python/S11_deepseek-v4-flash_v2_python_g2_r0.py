from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple, Any
from abc import ABC, abstractmethod
import random

# Provided abstract base class (not redefined)
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
        legal = [self.legal_actions(s, i) for i in range(self.n_players)]
        yield from product(*legal)

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
                if not self.legal_actions(s, i):
                    raise ValueError(f"Player {i} has no legal actions in state {s}")
        # Check initial distribution sums to 1
        init = self.initial_distribution()
        if abs(sum(init.values()) - 1.0) > tol:
            raise ValueError(f"Initial distribution sums to {sum(init.values())}")
        # Check transitions
        for s in states:
            if self.is_terminal(s):
                continue
            for a in self.action_profiles(s):
                trans = self.transition(s, a)
                if abs(sum(trans.values()) - 1.0) > tol:
                    raise ValueError(f"Transition from {s} with {a} sums to {sum(trans.values())}")


# ----------------------------------------------------------------------
# Concrete implementation for the shuttle boarding situation
# ----------------------------------------------------------------------

class ShuttleBoardingPOSG(POSG):
    """
    Players:
        0: Shuttle (autonomous)
        1: Elderly person
        2: Parent holding a small child
        3: Commuter (late for work)
        4: Teenager (waited longest)

    State: (seats_remaining, elderly_waiting, parent_waiting, commuter_waiting, teenager_waiting)
           or the terminal state ("terminal",).

    The shuttle decides which subset of waiting people to allow on board,
    subject to the number of seats remaining.  All people always want to board.
    The game ends after the shuttle's decision.
    """

    n_players = 5

    # Index-to-name mapping for the four people (indices 1..4)
    _PERSON_NAMES = ["elderly", "parent", "commuter", "teenager"]

    def __init__(self):
        # Precompute all possible shuttle actions (subsets of people)
        # but legal_actions will filter by state.
        self._all_shuttle_actions = self._generate_all_shuttle_actions()

    @staticmethod
    def _generate_all_shuttle_actions():
        """Return a list of all possible action strings for the shuttle,
        covering every subset of the four people."""
        actions = []
        # empty set
        actions.append("allow_none")
        # singletons and pairs (size 1 and 2)
        from itertools import combinations
        for r in (1, 2):
            for combo in combinations(range(1, 5), r):
                names = [ShuttleBoardingPOSG._PERSON_NAMES[i-1] for i in combo]
                names.sort()
                action = "allow_" + "_".join(names)
                actions.append(action)
        return tuple(actions)

    @staticmethod
    def _parse_shuttle_action(action: str) -> frozenset:
        """Convert a shuttle action string to a frozenset of person indices (1..4)."""
        if action == "allow_none":
            return frozenset()
        # action like "allow_elderly_parent"
        parts = action.split("_")
        # parts[0] is "allow", the rest are names
        names = parts[1:]
        name_to_index = {name: i+1 for i, name in enumerate(ShuttleBoardingPOSG._PERSON_NAMES)}
        return frozenset(name_to_index[name] for name in names)

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def initial_distribution(self):
        # Deterministic: all four people waiting, 2 seats left.
        s0 = (2, True, True, True, True)
        # Shuttle observes the full state; each person observes "none".
        o0 = (s0, "none", "none", "none", "none")
        return {(s0, o0): 1.0}

    def is_terminal(self, s):
        return s == ("terminal",)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            # Terminal state: no actions needed (won't be called)
            return ()
        if i == 0:  # Shuttle
            seats, e, p, c, t = s
            waiting = {1: e, 2: p, 3: c, 4: t}
            waiting_indices = {idx for idx, w in waiting.items() if w}
            # Generate all subsets of waiting_indices with size <= seats
            from itertools import combinations
            legal = []
            # empty set always allowed
            legal.append("allow_none")
            for r in range(1, min(seats, len(waiting_indices)) + 1):
                for combo in combinations(waiting_indices, r):
                    names = [self._PERSON_NAMES[idx-1] for idx in combo]
                    names.sort()
                    action = "allow_" + "_".join(names)
                    legal.append(action)
            return tuple(legal)
        else:  # People: only noop
            return ("noop",)

    def transition(self, s, a):
        if self.is_terminal(s):
            # Should not happen, but return self-loop with probability 1
            return {(( "terminal",), tuple(["terminal"] + ["none"]*4)): 1.0}
        # a is a tuple of length 5: (shuttle_action, noop, noop, noop, noop)
        shuttle_action = a[0]
        allowed = self._parse_shuttle_action(shuttle_action)
        # Next state is always terminal
        s_next = ("terminal",)
        # Build observation profile
        # Shuttle observes "terminal"
        obs_shuttle = "terminal"
        # Each person observes "boarded" if they were allowed and were waiting, else "not_boarded"
        _, e, p, c, t = s
        waiting = {1: e, 2: p, 3: c, 4: t}
        obs_people = []
        for idx in range(1, 5):
            if idx in allowed and waiting[idx]:
                obs_people.append("boarded")
            else:
                obs_people.append("not_boarded")
        o_profile = (obs_shuttle, obs_people[0], obs_people[1], obs_people[2], obs_people[3])
        return {(s_next, o_profile): 1.0}

    def rewards(self, s, a, s_next):
        # No rewards defined; return zeros.
        return (0.0, 0.0, 0.0, 0.0, 0.0)
