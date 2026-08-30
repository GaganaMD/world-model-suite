from posg import POSG

from typing import Sequence, Mapping, Iterator
from abc import ABC, abstractmethod
import random
# Assuming POSG is imported, but we need to define S, A, O as type vars? Actually the base class defines generic. So we can subclass as concrete.

class FactorySafety(POSG):
    n_players = 2
    
    # define states as strings or tuples
    _HUMAN_SKIPPED = ("skipped",)
    _HUMAN_FOLLOWED = ("followed",)
    _TERMINAL = "terminal"
    
    def initial_distribution(self):
        return {
            (self._HUMAN_SKIPPED, ("skipped", "skipped")): 0.5,
            (self._HUMAN_FOLLOWED, ("followed", "followed")): 0.5
        }
    
    def is_terminal(self, s):
        return s == self._TERMINAL
    
    def legal_actions(self, s, i):
        if s == self._TERMINAL:
            return ("noop",)  # but not used
        # non-terminal
        if i == 0:  # robot
            return ("intervene", "noop")
        else:  # human, i==1
            return ("noop",)
    
    def transition(self, s, a):
        if s == self._TERMINAL:
            return {(self._TERMINAL, ("none", "none")): 1.0}  # but shouldn't be called
        # From any non-terminal state, regardless of human's action (only noop) and robot's choice, go to terminal
        # a is (robot_action, human_action)
        return {(self._TERMINAL, ("none", "none")): 1.0}
    
    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
