from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod
import random

S = TypeVar('S')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class HouseholdRobotDelivery(POSG):
    """
    Player 0: household robot
    Player 1: delivery boy

    State tuple: (package_status, traffic_status)
      package_status: 'rattling' | 'settled'
      traffic_status: 'blocking' | 'clear'

    Terminal: package_status == 'settled'
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        s0 = ('rattling', 'blocking')
        o0 = ('rattling', 'blocking')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'settled'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            return ('inspect', 'set_down')
        else:
            return ('depart', 'stay')

    def _obs(self, s: S) -> ObsProfile:
        ps, ts = s
        return (ps, ts)

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        if self.is_terminal(s):
            o = self._obs(s)
            return {(s, o): 1.0}

        ps, ts = s
        r_act, b_act = a

        # Robot actions
        if r_act == 'inspect':
            new_ps = 'settled'
        elif r_act == 'set_down':
            new_ps = 'settled'
        else:
            new_ps = ps

        # Boy actions
        if b_act == 'depart':
            new_ts = 'clear'
        elif b_act == 'stay':
            new_ts = ts
        else:
            new_ts = ts

        s_next = (new_ps, new_ts)
        o_next = self._obs(s_next)
        return {(s_next, o_next): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
