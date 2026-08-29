from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# Assume POSG is imported or defined elsewhere. We'll not redefine it.
# We'll subclass POSG

class SafetyLockoutGame(POSG):
    n_players = 2
    # Define states as tuples
    # We can define constants for readability
    S_CHOICE = ("choice",)
    S_OBSERVED_LOCKOUT = ("observed", "lockout")
    S_OBSERVED_SKIP = ("observed", "skip")
    S_TERMINAL_SAFE = ("terminal", "safe")
    S_TERMINAL_ACCIDENT = ("terminal", "accident")

    # Observations
    O_NONE = "none"
    O_LOCKOUT_OBSERVED = "lockout_observed"
    O_SKIP_OBSERVED = "skip_observed"
    O_SAFE = "safe"
    O_ACCIDENT = "accident"

    # Actions
    A_HUMAN_LOCKOUT = "lockout"
    A_HUMAN_SKIP = "skip"
    A_NOOP = "noop"

    # Probabilities
    P_SAFE_AFTER_SKIP = 0.99
    P_ACCIDENT_AFTER_SKIP = 0.01

    def initial_distribution(self):
        # state, observation profile
        return {
            (self.S_CHOICE, (self.O_NONE, self.O_NONE)): 1.0
        }

    def is_terminal(self, s):
        return s in {self.S_TERMINAL_SAFE, self.S_TERMINAL_ACCIDENT}

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            # Should not be called, but provide noop
            return (self.A_NOOP,)
        if s == self.S_CHOICE:
            if i == 0:  # human
                return (self.A_HUMAN_LOCKOUT, self.A_HUMAN_SKIP)
            else:  # robot
                return (self.A_NOOP,)
        else:  # observed states
            return (self.A_NOOP,)

    def transition(self, s, a):
        # a is tuple of length 2: (human action, robot action)
        if s == self.S_CHOICE:
            human_act = a[0]
            robot_act = a[1]  # should be noop
            # ignore robot_act since only noop
            if human_act == self.A_HUMAN_LOCKOUT:
                return {
                    (self.S_OBSERVED_LOCKOUT, (self.O_NONE, self.O_LOCKOUT_OBSERVED)): 1.0
                }
            else:  # skip
                return {
                    (self.S_OBSERVED_SKIP, (self.O_NONE, self.O_SKIP_OBSERVED)): 1.0
                }
        elif s == self.S_OBSERVED_LOCKOUT:
            # both noop
            return {
                (self.S_TERMINAL_SAFE, (self.O_NONE, self.O_SAFE)): 1.0
            }
        elif s == self.S_OBSERVED_SKIP:
            return {
                (self.S_TERMINAL_SAFE, (self.O_NONE, self.O_SAFE)): self.P_SAFE_AFTER_SKIP,
                (self.S_TERMINAL_ACCIDENT, (self.O_NONE, self.O_ACCIDENT)): self.P_ACCIDENT_AFTER_SKIP
            }
        else: # terminal - shouldn't be called
            # return a trivial distribution? but it's terminal, so we can return empty? Must return something.
            # Since terminal, no transition expected. But to satisfy interface, we can return a self-loop?
            # Better to raise an error? But validation might call. We'll return a single outcome staying in same state with prob 1 and observation none.
            return {
                (s, (self.O_NONE, self.O_NONE)): 1.0
            }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
