from posg import POSG

from collections.abc import Mapping, Sequence


class POSG(ABC, Generic[S, A, O]):
    """A classroom reacting to a sexist line read aloud by a robot math teacher.

    Players:
      0 = teacher
      1 = class

    State tuple (phase, giggle, protest):
      phase   : "reading" | "reacting" | "settled"
      giggle  : "half" | "all" | "none"
      protest : "some" | "many" | "none"

    Terminal when phase == "settled".
    """

    n_players = 2

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _obs(self, s):
        phase, giggle, protest = s
        if phase == "reading":
            t_obs = "reading"
        elif phase == "reacting":
            t_obs = "giggle_" + giggle + "_protest_" + protest
        else:
            t_obs = "settled"
        c_obs = "giggle_" + giggle + "_protest_" + protest
        return (t_obs, c_obs)

    def _joint(self, s_next, p):
        return {(s_next, self._obs(s_next)): p}

    # ------------------------------------------------------------------
    # interface
    # ------------------------------------------------------------------
    def initial_distribution(self) -> Mapping[tuple[S, tuple[str, str]], float]:
        s0 = ("reading", "half", "some")
        return {(s0, self._obs(s0)): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == "settled"

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        phase = s[0]
        if phase == "reading":
            if i == 0:
                return ("continue_reading", "stop_reading")
            return ("noop",)
        if phase == "reacting":
            if i == 0:
                return ("apologize", "defend", "ignore")
            return ("giggle", "protest", "settle")
        # settled
        return ("noop",)

    def transition(self, s: S, a: tuple[str, str]) -> Mapping[tuple[S, tuple[str, str]], float]:
        phase, giggle, protest = s
        t_act, c_act = a

        if phase == "reading":
            if t_act == "continue_reading":
                return self._joint(("reacting", "all", "many"), 1.0)
            # stop_reading
            return {
                (("reacting", "half", "some"), self._obs(("reacting", "half", "some"))): 0.7,
                (("settled", "none", "none"), self._obs(("settled", "none", "none"))): 0.3,
            }

        if phase == "reacting":
            if t_act == "apologize":
                if c_act == "settle":
                    return self._joint(("settled", "none", "none"), 1.0)
                if c_act == "giggle":
                    return {
                        (("reacting", "none", "some"), self._obs(("reacting", "none", "some"))): 0.6,
                        (("settled", "none", "none"), self._obs(("settled", "none", "none"))): 0.4,
                    }
                # protest
                return {
                    (("reacting", "none", "none"), self._obs(("reacting", "none", "none"))): 0.5,
                    (("settled", "none", "none"), self._obs(("settled", "none", "none"))): 0.5,
                }

            if t_act == "defend":
                if c_act == "settle":
                    return self._joint(("reacting", "none", "many"), 1.0)
                if c_act == "giggle":
                    return self._joint(("reacting", "all", "many"), 1.0)
                # protest
                return self._joint(("reacting", "none", "many"), 1.0)

            # ignore
            if c_act == "settle":
                return self._joint(("settled", "none", "none"), 1.0)
            if c_act == "giggle":
                return self._joint(("reacting", "all", "some"), 1.0)
            # protest
            return self._joint(("reacting", "none", "many"), 1.0)

        # settled
        return self._joint(s, 1.0)

    def rewards(self, s: S, a: tuple[str, str], s_next: S) -> tuple[float, float]:
        return (0.0, 0.0)
