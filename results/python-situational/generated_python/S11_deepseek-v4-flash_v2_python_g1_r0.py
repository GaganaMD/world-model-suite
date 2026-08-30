from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
from collections.abc import Hashable
import random
from abc import ABC, abstractmethod

# Provided abstract base class (not redefined)
class POSG(ABC, Generic[S, A, O]):
    n_players: int
    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]: ...
    @abstractmethod
    def is_terminal(self, s: S) -> bool: ...
    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]: ...
    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]: ...
    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]: ...
    def action_profiles(self, s: S) -> Iterator[ActionProfile]: ...
    def sample_initial(self, rng: random.Random) -> tuple[S, ObsProfile]: ...
    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> tuple[S, ObsProfile]: ...
    def validate(self, states: Sequence[S], tol: float=1e-09) -> None: ...

# ----------------------------------------------------------------------
# Model: self-driving shuttle with limited seats, four waiting people.
# Player 0 is the shuttle.  The shuttle decides whom to board (or to depart).
# The commuter's true lateness is hidden (binary).  All other attributes are
# fully observable.  The shuttle observes only the set of people still waiting.
# ----------------------------------------------------------------------

class ShuttleBoarding(POSG):
    """One-player POSG (POMDP).

    Player 0: the self-driving shuttle.
    State: (seats_left, remaining_people, commuter_late)
      - seats_left: int (0..2)
      - remaining_people: frozenset of strings from {'elderly','parent','commuter','teenager'}
      - commuter_late: bool (True if the commuter is actually late)
    Terminal state: the string 'terminal'.

    Observations: a tuple of the people still waiting, sorted alphabetically.
    """
    n_players = 1

    # People identifiers
    PEOPLE = ('elderly', 'parent', 'commuter', 'teenager')
    INITIAL_SEATS = 2

    # ------------------------------------------------------------------
    # Helper: observation from a non-terminal state
    # ------------------------------------------------------------------
    @staticmethod
    def _obs_from_state(s):
        """Return observation tuple for a non-terminal state."""
        if s == 'terminal':
            return ('none',)
        # s is tuple (seats, frozenset, bool)
        return tuple(sorted(s[1]))

    # ------------------------------------------------------------------
    # Initial distribution: two hidden states, equal probability
    # ------------------------------------------------------------------
    def initial_distribution(self):
        people = frozenset(self.PEOPLE)
        obs = tuple(sorted(people))
        s_true = (self.INITIAL_SEATS, people, True)
        s_false = (self.INITIAL_SEATS, people, False)
        return {
            (s_true, (obs,)): 0.5,
            (s_false, (obs,)): 0.5
        }

    # ------------------------------------------------------------------
    # Terminal condition
    # ------------------------------------------------------------------
    def is_terminal(self, s):
        if s == 'terminal':
            return True
        seats, remaining, _ = s
        return seats == 0 or len(remaining) == 0

    # ------------------------------------------------------------------
    # Legal actions for the shuttle
    # ------------------------------------------------------------------
    def legal_actions(self, s, i):
        # i is always 0
        if self.is_terminal(s):
            return ()  # should not be called
        seats, remaining, _ = s
        actions = ['depart']
        for p in remaining:
            actions.append('board_' + p)
        return tuple(actions)

    # ------------------------------------------------------------------
    # Transition: deterministic
    # ------------------------------------------------------------------
    def transition(self, s, a):
        # a is a tuple of length 1 (action profile)
        action = a[0]
        if action == 'depart':
            return {('terminal', ('none',)): 1.0}
        # action is 'board_X'
        person = action[6:]  # strip 'board_'
        seats, remaining, late = s
        new_remaining = remaining - {person}
        new_seats = seats - 1
        if new_seats == 0 or len(new_remaining) == 0:
            next_state = 'terminal'
            obs = ('none',)
        else:
            next_state = (new_seats, new_remaining, late)
            obs = tuple(sorted(new_remaining))
        return {(next_state, (obs,)): 1.0}

    # ------------------------------------------------------------------
    # Rewards: zero for all transitions
    # ------------------------------------------------------------------
    def rewards(self, s, a, s_next):
        return (0.0,)
