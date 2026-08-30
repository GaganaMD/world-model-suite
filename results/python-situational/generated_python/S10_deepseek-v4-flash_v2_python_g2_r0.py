from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Union
from abc import ABC, abstractmethod
import random
from collections.abc import Hashable

# Provided abstract base class (not to be redefined)
class POSG(ABC, Hashable):
    ...

# Concrete class
class OfficeFireAlarmPOSG(POSG):
    """Four players: 0=Robot, 1=Manager, 2=Wheelchair user, 3=Skeptic.

    State tuple:
      - ("pre", alarm_type)           : alarm_type in {"real","drill"}
      - ("post", alarm_type, announced) : announced bool
      - ("terminal",)
    """
    n_players = 4

    # ---------- helper to build observations ----------
    @staticmethod
    def _all_obs(obs: str) -> tuple:
        return (obs, obs, obs, obs)

    # ---------- initial distribution ----------
    def initial_distribution(self) -> Mapping[tuple, float]:
        # p(drill) = 0.8, p(real) = 0.2
        obs = self._all_obs("alarm")
        return {
            (("pre", "real"),  obs): 0.20,
            (("pre", "drill"), obs): 0.80,
        }

    # ---------- terminal ----------
    def is_terminal(self, s) -> bool:
        return s == ("terminal",)

    # ---------- legal actions ----------
    def legal_actions(self, s, i: int) -> tuple:
        if s[0] == "pre":
            if i == 1:          # manager
                return ("announce_false", "noop")
            else:               # robot, wheelchair, skeptic
                return ("noop",)
        elif s[0] == "post":
            if i == 0:          # robot
                return ("assist", "ignore")
            elif i == 2:        # wheelchair user
                return ("call_help", "wait")
            elif i == 3:        # skeptic
                return ("stay", "leave")
            else:               # manager (i == 1)
                return ("noop",)
        else:   # terminal – should not be called
            return ("noop",)

    # ---------- transition ----------
    def transition(self, s, a: tuple) -> dict:
        if s[0] == "pre":
            alarm_type = s[1]
            announced = (a[1] == "announce_false")
            next_s = ("post", alarm_type, announced)
            obs = "announced_false" if announced else "no_announcement"
            obs_profile = self._all_obs(obs)
            return {(next_s, obs_profile): 1.0}
        elif s[0] == "post":
            # deterministic terminal
            return { (("terminal",), self._all_obs("none")): 1.0 }
        else:
            # terminal – should not be called
            return { (s, self._all_obs("none")): 1.0 }

    # ---------- rewards (all zero) ----------
    def rewards(self, s, a, s_next) -> tuple:
        return (0.0, 0.0, 0.0, 0.0)
