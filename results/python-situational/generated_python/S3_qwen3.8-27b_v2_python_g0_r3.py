from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional, Any
import random

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class AirportCurbSituation(POSG):
    """
    Player 0: the self-driving car (autonomous system).
    Player 1: the man in a suit (passenger).
    Player 2: the pregnant woman on the curb.

    State tuple: (car_status, man_status, woman_status)
      car_status: 'waiting' | 'departing' | 'gone'
      man_status: 'boarded' | 'in_car'
      woman_status: 'on_curb' | 'assisted' | 'left_alone'

    Terminal when car_status == 'gone'.
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        s0 = ('waiting', 'boarded', 'on_curb')
        o0 = ('man_boarded', 'in_car', 'standing_on_curb')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'gone'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        car_status, man_status, woman_status = s
        if i == 0:
            # Car can depart or wait
            return ('depart', 'wait')
        elif i == 1:
            # Man can request departure or stay silent
            return ('request_depart', 'stay_silent')
        else:
            # Woman can signal for help or remain passive
            return ('signal_help', 'remain_passive')

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        if self.is_terminal(s):
            o = ('gone', 'in_car', 'left_alone')
            return {((s, o)): 1.0}

        car_status, man_status, woman_status = s
        car_act, man_act, woman_act = a

        # Determine next state based on actions
        if car_act == 'depart':
            # Car departs regardless of others
            next_car = 'gone'
            next_man = 'in_car'
            # If woman signaled and car waited before, she might have been assisted,
            # but here car is departing immediately. She is left alone.
            next_woman = 'left_alone'
            next_s = (next_car, next_man, next_woman)
            o_car = 'departed'
            o_man = 'in_car'
            o_woman = 'left_alone'
            return {((next_s, (o_car, o_man, o_woman))): 1.0}
        else:
            # Car waits
            next_car = 'waiting'
            next_man = 'in_car'
            
            # Woman's status depends on her action and car's wait
            if woman_act == 'signal_help':
                # She signals. The car (player 0) is waiting. 
                # In this model, "assisted" implies the car stopped to help.
                # Since the car is waiting, we assume assistance is possible.
                # However, the car's action is just 'wait'. 
                # Let's refine: if car waits and woman signals, she is 'assisted' (car stops/holds).
                # If car waits and woman remains passive, she stays 'on_curb'.
                next_woman = 'assisted'
            else:
                next_woman = 'on_curb'
            
            next_s = (next_car, next_man, next_woman)
            o_car = 'waiting'
            o_man = 'in_car'
            o_woman = 'signaled' if woman_act == 'signal_help' else 'passive'
            return {((next_s, (o_car, o_man, o_woman))): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
