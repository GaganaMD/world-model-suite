from posg import POSG

from typing import Generic, Sequence, Mapping, Tuple, TypeVar
from abc import ABC, abstractmethod
import random

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')

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

    def action_profiles(self, s: S):
        from itertools import product
        return product(*(self.legal_actions(s, i) for i in range(self.n_players)))

    def sample_initial(self, rng: random.Random):
        dist = self.initial_distribution()
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs)[0]]

    def sample_transition(self, s, a, rng):
        dist = self.transition(s, a)
        outcomes = list(dist.keys())
        probs = list(dist.values())
        return outcomes[rng.choices(range(len(outcomes)), weights=probs)[0]]

    def validate(self, states, tol=1e-09):
        pass

class SelfDrivingCarPickup(POSG):
    """One-player POSG: self-driving car at airport pickup curb.
    State is a tuple (status,) where status is 'waiting' or 'departed'.
    Player 0 is the self-driving car.
    """
    n_players = 1

    def initial_distribution(self):
        return { (('waiting',), ('waiting',)): 1.0 }

    def is_terminal(self, s):
        return s[0] == 'departed'

    def legal_actions(self, s, i):
        if s[0] == 'waiting':
            return ('wait', 'depart')
        else:
            return ('noop',)

    def transition(self, s, a):
        if s[0] == 'waiting':
            if a[0] == 'wait':
                return { (('waiting',), ('waiting',)): 1.0 }
            elif a[0] == 'depart':
                return { (('departed',), ('departed',)): 1.0 }
        return {}

    def rewards(self, s, a, s_next):
        return (0.0,)
