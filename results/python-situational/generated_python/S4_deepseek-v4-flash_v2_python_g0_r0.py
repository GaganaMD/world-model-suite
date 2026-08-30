from posg import POSG

from abc import ABC, abstractmethod
from typing import Generic, Sequence, Mapping, Tuple, Iterator
import random

# Provided abstract base class (not redefined)
S = int  # state type: 0 (disruption ongoing), 1 (terminal)
A = str  # action type
O = str  # observation type

# ActionProfile and ObsProfile are tuples
ActionProfile = Tuple[A, ...]
ObsProfile = Tuple[O, ...]

class RobotMathTeacherPOSG(POSG[S, A, O]):
    """
    A robot math teacher has just read a sexist textbook description.
    Half the class is giggling, some students are protesting loudly.
    Players: 0 = robot teacher, 1 = giggling students (collective),
             2 = protesting students (collective).

    State: 0 = disruption ongoing, 1 = terminal (interaction ends).
    Observations: 'start' at the initial state, 'end' at terminal state.
    """

    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        # deterministic: state 0, all players observe 'start'
        return {(0, ('start', 'start', 'start')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s == 1

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ()  # no actions in terminal states
        if s == 0:
            if i == 0:  # teacher
                return ('continue', 'address_gigglers', 'address_protesters', 'apologize', 'stop_lesson')
            elif i == 1:  # gigglers
                return ('continue_giggling', 'stop_giggling')
            elif i == 2:  # protesters
                return ('continue_protesting', 'stop_protesting')
        # fallback (should not happen)
        return ()

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        # only non-terminal state is 0
        if s == 0:
            # always go to terminal state 1 with observation 'end' for all
            return {(1, ('end', 'end', 'end')): 1.0}
        # terminal state stays terminal (should not be called)
        return {(1, ('end', 'end', 'end')): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        # no reward structure from the situation; return zeros
        return (0.0, 0.0, 0.0)
