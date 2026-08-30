from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional, Any, Union

S = Tuple[str, str, str]
A = str
O = str


class POSG(ABC, Generic[S, A, O]):
    """Two-player simultaneous-move POSG.

    Player 0: the self-driving car (the driver).
    Player 1: the pregnant woman on the curb.

    State tuple (phase, car_status, woman_status):
      phase: 'curb' | 'road' | 'terminal'
      car_status: 'idle' | 'moving'
      woman_status: 'standing' | 'assisted' | 'unassisted'

    Terminal when phase == 'terminal'.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        s0 = ('curb', 'idle', 'standing')
        o0 = ('boarded', 'standing')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'terminal'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # car: depart or offer assistance
            return ('depart', 'offer_assistance')
        else:
            # woman: accept or decline
            return ('accept', 'decline')

    def transition(self, s: S, a: Tuple[A, A]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        if self.is_terminal(s):
            return {((s, ('none', 'none')): 1.0}
        car_a, woman_a = a
        if car_a == 'depart':
            ns = ('terminal', 'moving', 'unassisted')
            obs = ('departed', 'unassisted')
            return {((ns, obs)): 1.0}
        else:  # offer_assistance
            if woman_a == 'accept':
                ns = ('terminal', 'moving', 'assisted')
                obs = ('assisted', 'accepted')
            else:
                ns = ('terminal', 'moving', 'unassisted')
                obs = ('unassisted', 'declined')
            return {((ns, obs)): 1.0}

    def rewards(self, s: S, a: Tuple[A, A], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
