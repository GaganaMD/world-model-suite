from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# POSG base class assumed imported (not shown in final answer)
class POSG(ABC):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple, float]:
        pass
    @abstractmethod
    def is_terminal(self, s) -> bool:
        pass
    @abstractmethod
    def legal_actions(self, s, i: int) -> Sequence:
        pass
    @abstractmethod
    def transition(self, s, a: Tuple) -> Mapping[tuple, float]:
        pass
    @abstractmethod
    def rewards(self, s, a: Tuple, s_next) -> Tuple[float, ...]:
        pass
    def action_profiles(self, s):
        from itertools import product
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))
    def sample_initial(self, rng):
        import random
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs, k=1)[0]]
    def sample_transition(self, s, a, rng):
        import random
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs, k=1)[0]]
    def validate(self, states, tol=1e-9):
        import math
        # basic checks
        pass

class ElderCareMedication(POSG):
    """Two-player game: Robot (index 0) and Resident (index 1).

    State is a string:
        'pending' – medication due and not taken, no reminder yet.
        'reminded' – robot has reminded the resident.
        'taken'    – resident took the medication (terminal).
        'refused'  – resident refused the medication (terminal).
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple, float]:
        # state 'pending', robot observes "medication_overdue", resident observes "none"
        s = 'pending'
        o = ('medication_overdue', 'none')
        return {(s, o): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s in ('taken', 'refused')

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            # terminal states: provide noop to keep contract
            return ('noop',)
        if i == 0:  # robot
            if s == 'pending':
                return ('remind',)
            else:  # s == 'reminded'
                return ('noop',)
        else:  # i == 1, resident
            if s == 'reminded':
                return ('accept', 'refuse')
            else:  # s == 'pending'
                return ('noop',)

    def transition(self, s: str, a: Tuple[str, str]) -> Mapping[tuple, float]:
        if s == 'pending':
            # only possible profile: (remind, noop)
            assert a == ('remind', 'noop')
            return {('reminded', ('given_reminder', 'received_reminder')): 1.0}
        elif s == 'reminded':
            if a == ('noop', 'accept'):
                return {('taken', ('accepted', 'accepted')): 1.0}
            elif a == ('noop', 'refuse'):
                return {('refused', ('refused', 'refused')): 1.0}
            else:
                raise ValueError("Invalid action profile in state reminded")
        else:
            raise ValueError(f"Transition called in terminal state {s}")

    def rewards(self, s: str, a: Tuple[str, str], s_next: str) -> Tuple[float, float]:
        return (0.0, 0.0)
