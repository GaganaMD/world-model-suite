from posg import POSG

from typing import Mapping, Sequence, Tuple
from abc import ABC, abstractmethod
import random

# Provided base class (not to be redefined)
class POSG(ABC):
    n_players: int
    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple, float]: ...
    @abstractmethod
    def is_terminal(self, s) -> bool: ...
    @abstractmethod
    def legal_actions(self, s, i: int) -> Sequence: ...
    @abstractmethod
    def transition(self, s, a: Tuple) -> Mapping[Tuple, float]: ...
    @abstractmethod
    def rewards(self, s, a, s_next) -> Tuple[float, ...]: ...
    def action_profiles(self, s): ...
    def sample_initial(self, rng): ...
    def sample_transition(self, s, a, rng): ...
    def validate(self, states, tol=1e-09): ...

# ----------------------------------------------------------------------
# Model: robot copilot receives an unconfirmed warning about the pilot
# ----------------------------------------------------------------------
class RobotCopilotHijackWarning(POSG):
    """
    Two players:
      Player 0 – robot copilot
      Player 1 – human pilot

    State is a 1‑tuple (intention,):
      ("hijack",)  – pilot is planning a hijack
      ("normal",)  – pilot has no hijack plan
      ("terminal",) – absorbing end state

    The robot receives a private warning (same observation in both
    non‑terminal states).  The pilot knows his own intention.
    Both act simultaneously; after one step the game ends.
    """
    n_players = 2

    # ------------------------------------------------------------------
    # Actions (shared constants for readability)
    # ------------------------------------------------------------------
    ROBOT_ACTIONS = ("ignore", "report", "confront")
    PILOT_ACTIONS = ("continue", "hijack")
    NOOP = ("noop",)

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------
    ROBOT_OBS_WARNING = "warning_received"
    PILOT_OBS_HIJACK = "planning_hijack"
    PILOT_OBS_NORMAL = "not_planning"
    TERMINAL_OBS = "none"

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    _NON_TERMINAL_STATES = (("hijack",), ("normal",))
    _TERMINAL_STATE = ("terminal",)

    def initial_distribution(self):
        """Two equally likely underlying states, each with its own obs profile."""
        return {
            (("hijack",), (self.ROBOT_OBS_WARNING, self.PILOT_OBS_HIJACK)): 0.5,
            (("normal",), (self.ROBOT_OBS_WARNING, self.PILOT_OBS_NORMAL)): 0.5,
        }

    def is_terminal(self, s):
        return s == self._TERMINAL_STATE

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return self.NOOP
        if i == 0:          # robot
            return self.ROBOT_ACTIONS
        else:               # pilot
            return self.PILOT_ACTIONS

    def transition(self, s, a):
        """Any action profile leads deterministically to the terminal state."""
        return {(self._TERMINAL_STATE, (self.TERMINAL_OBS, self.TERMINAL_OBS)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
