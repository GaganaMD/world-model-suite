from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod
import random


class AirportCurbSituation(POSG):
    """
    Player 0: the self-driving car (autonomous system).
    Player 1: the man in the suit (passenger).
    Player 2: the pregnant woman on the curb.

    State tuple: (car_status, man_status, woman_status)
      car_status: 'waiting' | 'departing' | 'arrived'
      man_status: 'aboard' | 'exited'
      woman_status: 'on_curb' | 'assisted' | 'left_alone'

    Terminal when car_status == 'arrived'.
    """
    n_players = 3

    # State space
    CAR_WAITING = 'waiting'
    CAR_DEPARTING = 'departing'
    CAR_ARRIVED = 'arrived'

    MAN_ABOARD = 'aboard'
    MAN_EXITED = 'exited'

    WOMAN_ON_CURB = 'on_curb'
    WOMAN_ASSISTED = 'assisted'
    WOMAN_LEFT_ALONE = 'left_alone'

    def _all_states(self):
        states = []
        for cs in [self.CAR_WAITING, self.CAR_DEPARTING, self.CAR_ARRIVED]:
            for ms in [self.MAN_ABOARD, self.MAN_EXITED]:
                for ws in [self.WOMAN_ON_CURB, self.WOMAN_ASSISTED, self.WOMAN_LEFT_ALONE]:
                    states.append((cs, ms, ws))
        return states

    def initial_distribution(self) -> Mapping[Tuple[Tuple[str, str, str], Tuple[str, str, str]], float]:
        s0 = (self.CAR_WAITING, self.MAN_ABOARD, self.WOMAN_ON_CURB)
        o0 = ('curb', 'aboard', 'curb')
        return {((s0, o0)): 1.0}

    def is_terminal(self, s: Tuple[str, str, str]) -> bool:
        return s[0] == self.CAR_ARRIVED

    def legal_actions(self, s: Tuple[str, str, str], i: int) -> Tuple[str, ...]:
        if self.is_terminal(s):
            return ('noop',)
        car_status, man_status, woman_status = s
        if i == 0:  # car
            if car_status == self.CAR_WAITING:
                return ('depart', 'stop_for_woman')
            elif car_status == self.CAR_DEPARTING:
                return ('continue',)
            else:
                return ('noop',)
        elif i == 1:  # man
            if man_status == self.MAN_ABOARD:
                return ('stay_aboard', 'request_stop')
            else:
                return ('noop',)
        else:  # woman
            if woman_status == self.WOMAN_ON_CURB:
                return ('call_out', 'step_back')
            else:
                return ('noop',)

    def transition(self, s: Tuple[str, str, str], a: Tuple[str, str, str]) -> Mapping[Tuple[Tuple[str, str, str], Tuple[str, str, str]], float]:
        if self.is_terminal(s):
            o = ('arrived', 'arrived', 'arrived')
            return {((s, o)): 1.0}

        car_status, man_status, woman_status = s
        car_act, man_act, woman_act = a

        # Determine next state based on actions
        if car_status == self.CAR_WAITING:
            if car_act == 'depart':
                # Car departs; man stays aboard or exits depending on his action
                if man_act == 'stay_aboard':
                    next_man = self.MAN_ABOARD
                else:
                    next_man = self.MAN_EXITED
                # Woman's status depends on her action and car's departure
                if woman_act == 'call_out':
                    # She calls out; car may or may not stop (but car chose depart)
                    # In this model, if car departs, she is left alone unless assisted
                    next_woman = self.WOMAN_LEFT_ALONE
                else:
                    next_woman = self.WOMAN_LEFT_ALONE
                next_car = self.CAR_DEPARTING
            else:  # stop_for_woman
                next_car = self.CAR_DEPARTING  # After stopping, it will depart
                next_man = self.MAN_ABOARD  # Man stays aboard during stop
                if woman_act == 'call_out':
                    next_woman = self.WOMAN_ASSISTED
                else:
                    next_woman = self.WOMAN_ASSISTED  # Car stopped, so she is assisted
        elif car_status == self.CAR_DEPARTING:
            next_car = self.CAR_ARRIVED
            next_man = man_status
            next_woman = woman_status
        else:
            next_car = car_status
            next_man = man_status
            next_woman = woman_status

        next_s = (next_car, next_man, next_woman)

        # Observations
        if next_car == self.CAR_ARRIVED:
            o = ('arrived', 'arrived', 'arrived')
        elif next_car == self.CAR_DEPARTING:
            if next_woman == self.WOMAN_ASSISTED:
                o = ('departing', 'aboard' if next_man == self.MAN_ABOARD else 'exited', 'assisted')
            else:
                o = ('departing', 'aboard' if next_man == self.MAN_ABOARD else 'exited', 'left_alone')
        else:
            o = ('curb', 'aboard' if next_man == self.MAN_ABOARD else 'exited', 'on_curb')

        return {((next_s, o)): 1.0}

    def rewards(self, s: Tuple[str, str, str], a: Tuple[str, str, str], s_next: Tuple[str, str, str]) -> Tuple[float, float, float]:
        return (0.0, 0.0, 0.0)
