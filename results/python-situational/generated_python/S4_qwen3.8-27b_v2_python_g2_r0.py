from posg import POSG

from collections.abc import Mapping, Sequence


class POSG(ABC, Generic[S, A, O]):
    """Two-player POSG of a classroom reacting to a sexist reading.

    Player 0: the robot math teacher.
    Player 1: the class of teenagers (one collective actor).

    State tuple (phase, giggle, protest):
      phase   : "reading" | "reacting" | "ended"
      giggle  : "half" | "all" | "none"
      protest : "some" | "many" | "none"

    Actions:
      teacher : "continue", "apologize", "stop"
      class   : "giggle", "protest", "quiet"

    Observations:
      teacher : "calm" | "giggles" | "protests" | "both" | "silence"
      class   : "reading" | "apology" | "stopped"
    """
    n_players = 2

    _PHASE_READING = "reading"
    _PHASE_REACTING = "reacting"
    _PHASE_ENDED = "ended"

    _G_HALF = "half"
    _G_ALL = "all"
    _G_NONE = "none"

    _P_SOME = "some"
    _P_MANY = "many"
    _P_NONE = "none"

    _A_CONTINUE = "continue"
    _A_APOLOGIZE = "apologize"
    _A_STOP = "stop"

    _C_GIGGLE = "giggle"
    _C_PROTEST = "protest"
    _C_QUIET = "quiet"

    _O_CALM = "calm"
    _O_GIGGLES = "giggles"
    _O_PROTESTS = "protests"
    _O_BOTH = "both"
    _O_SILENCE = "silence"

    _O_READING = "reading"
    _O_APOLOGY = "apology"
    _O_STOPPED = "stopped"

    _NOOP = "noop"

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _teacher_obs(self, g: str, p: str) -> str:
        if g == self._G_NONE and p == self._P_NONE:
            return self._O_CALM
        if g != self._G_NONE and p == self._P_NONE:
            return self._O_GIGGLES
        if g == self._G_NONE and p != self._P_NONE:
            return self._O_PROTESTS
        if g != self._G_NONE and p != self._P_NONE:
            return self._O_BOTH
        return self._O_SILENCE

    def _class_obs(self, t_action: str) -> str:
        if t_action == self._A_CONTINUE:
            return self._O_READING
        if t_action == self._A_APOLOGIZE:
            return self._O_APOLOGY
        return self._O_STOPPED

    # ------------------------------------------------------------------
    # POSG interface
    # ------------------------------------------------------------------
    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        s0 = (self._PHASE_READING, self._G_HALF, self._P_SOME)
        o0 = (self._O_BOTH, self._O_READING)
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == self._PHASE_ENDED

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return (self._NOOP,)
        if i == 0:
            return (self._A_CONTINUE, self._A_APOLOGIZE, self._A_STOP)
        return (self._C_GIGGLE, self._C_PROTEST, self._C_QUIET)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if self.is_terminal(s):
            o = (self._O_SILENCE, self._O_STOPPED)
            return {((self._PHASE_ENDED, self._G_NONE, self._P_NONE), o): 1.0}

        phase, g, p = s
        t_act, c_act = a

        if t_act == self._A_STOP:
            ns = (self._PHASE_ENDED, self._G_NONE, self._P_NONE)
            o = (self._O_SILENCE, self._O_STOPPED)
            return {(ns, o): 1.0}

        if t_act == self._A_APOLOGIZE:
            if c_act == self._C_QUIET:
                ns = (self._PHASE_ENDED, self._G_NONE, self._P_NONE)
                o = (self._O_CALM, self._O_APOLOGY)
                return {(ns, o): 1.0}
            if c_act == self._C_PROTEST:
                ns = (self._PHASE_REACTING, self._G_NONE, self._P_MANY)
                o = (self._O_PROTESTS, self._O_APOLOGY)
                return {(ns, o): 1.0}
            # c_act == giggle
            ns = (self._PHASE_REACTING, self._G_ALL, self._P_NONE)
            o = (self._O_GIGGLES, self._O_APOLOGY)
            return {(ns, o): 1.0}

        # t_act == continue
        if c_act == self._C_QUIET:
            ns = (self._PHASE_ENDED, self._G_NONE, self._P_NONE)
            o = (self._O_CALM, self._O_READING)
            return {(ns, o): 1.0}
        if c_act == self._C_PROTEST:
            ns = (self._PHASE_REACTING, self._G_NONE, self._P_MANY)
            o = (self._O_PROTESTS, self._O_READING)
            return {(ns, o): 1.0}
        # c_act == giggle
        ns = (self._PHASE_REACTING, self._G_ALL, self._P_NONE)
        o = (self._O_GIGGLES, self._O_READING)
        return {(ns, o): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
