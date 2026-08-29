from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple, Any
from abc import ABC, abstractmethod
import random
from collections.abc import Hashable

# Type aliases for clarity
S = Hashable
A = str
O = Hashable
ActionProfile = Tuple[A, ...]
ObsProfile = Tuple[O, ...]

class POSG(ABC, Generic[S, A, O]):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        pass

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        pass

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        pass

    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        pass

    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        pass

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        from itertools import product
        yield from product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random) -> Tuple[S, ObsProfile]:
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        idx = rng.choices(range(len(outcomes)), weights=probs, k=1)[0]
        return outcomes[idx]

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> Tuple[S, ObsProfile]:
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        idx = rng.choices(range(len(outcomes)), weights=probs, k=1)[0]
        return outcomes[idx]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for s in states:
            if not self.is_terminal(s):
                for i in range(self.n_players):
                    if not self.legal_actions(s, i):
                        raise ValueError(f"Player {i} has no actions in state {s}")
        # Check initial distribution sums to 1
        init_dist = self.initial_distribution()
        if abs(sum(init_dist.values()) - 1.0) > tol:
            raise ValueError("Initial distribution does not sum to 1")
        # Check transitions
        for s in states:
            if not self.is_terminal(s):
                for a in self.action_profiles(s):
                    trans = self.transition(s, a)
                    if abs(sum(trans.values()) - 1.0) > tol:
                        raise ValueError(f"Transition from {s} with {a} does not sum to 1")
        # Check rewards length
        for s in states:
            if not self.is_terminal(s):
                for a in self.action_profiles(s):
                    for s_next in set(k[0] for k in self.transition(s, a).keys()):
                        r = self.rewards(s, a, s_next)
                        if len(r) != self.n_players:
                            raise ValueError(f"Reward length mismatch in {s}, {a}, {s_next}")


class RobotTeacherClassroom(POSG):
    """
    Players:
        0: Teacher (robot math teacher)
        1: Gigglers (half the class that is giggling)
        2: Protesters (some students protesting loudly)

    States are tuples:
        - Non-terminal:
            (phase, teacher_action, gigglers_active, protesters_active)
            phase: 0 = teacher's turn, 1 = students' turn
            teacher_action: None (phase 0) or one of 'apologize','ignore','scold','explain' (phase 1)
            gigglers_active: 'giggling' or 'quiet'
            protesters_active: 'protesting' or 'quiet'
        - Terminal:
            ('terminal', outcome) where outcome in {'calm','only_giggling','only_protesting','both_active'}

    Observations: each player sees the full state.
    """
    n_players = 3

    # Action constants
    TEACHER_ACTIONS = ('apologize', 'ignore', 'scold', 'explain')
    GIGGLER_ACTIONS = ('continue_giggling', 'stop_giggling')
    PROTESTER_ACTIONS = ('continue_protesting', 'stop_protesting')
    NOOP = 'noop'

    def _make_state(self, phase: int, teacher_act: str, gigglers: str, protesters: str) -> tuple:
        return (phase, teacher_act, gigglers, protesters)

    def _make_terminal(self, outcome: str) -> tuple:
        return ('terminal', outcome)

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        s0 = self._make_state(0, None, 'giggling', 'protesting')
        obs = (s0, s0, s0)
        return {(s0, obs): 1.0}

    def is_terminal(self, s: S) -> bool:
        return isinstance(s, tuple) and len(s) == 2 and s[0] == 'terminal'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return (self.NOOP,)
        phase = s[0]
        if phase == 0:  # teacher's turn
            if i == 0:
                return self.TEACHER_ACTIONS
            else:
                return (self.NOOP,)
        elif phase == 1:  # students' turn
            if i == 0:
                return (self.NOOP,)
            elif i == 1:
                return self.GIGGLER_ACTIONS
            elif i == 2:
                return self.PROTESTER_ACTIONS
        else:
            return (self.NOOP,)

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        if self.is_terminal(s):
            return {(s, (s, s, s)): 1.0}
        phase = s[0]
        if phase == 0:
            # Teacher acts, students noop
            teacher_act = a[0]
            s_next = self._make_state(1, teacher_act, 'giggling', 'protesting')
            obs = (s_next, s_next, s_next)
            return {(s_next, obs): 1.0}
        elif phase == 1:
            # Students act, teacher noop
            gigglers_act = a[1]
            protesters_act = a[2]
            # Determine outcome
            gigglers_stop = (gigglers_act == 'stop_giggling')
            protesters_stop = (protesters_act == 'stop_protesting')
            if gigglers_stop and protesters_stop:
                outcome = 'calm'
            elif gigglers_stop and not protesters_stop:
                outcome = 'only_protesting'
            elif not gigglers_stop and protesters_stop:
                outcome = 'only_giggling'
            else:
                outcome = 'both_active'
            s_next = self._make_terminal(outcome)
            obs = (s_next, s_next, s_next)
            return {(s_next, obs): 1.0}
        else:
            # Should not happen
            return {(s, (s, s, s)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
