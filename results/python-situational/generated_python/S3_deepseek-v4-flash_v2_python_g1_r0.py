from posg import POSG

from typing import Sequence, Mapping, Tuple
from abc import ABC, abstractmethod
import random

class AirportPickupDilemma(POSG):
    """Three-player POSG: self-driving car (0), man in suit (1), pregnant woman (2).

    At an airport pickup curb the car waits with the man already inside.
    A woman who looks ill stands next to the car. Players act simultaneously
    once; then the game ends in a terminal state describing what happened.

    State is a single string 'waiting' (non‑terminal) or one of the terminal
    outcome strings listed in the transition map.
    """
    n_players = 3

    def initial_distribution(self):
        return { (('waiting', ('scene', 'scene', 'scene'))): 1.0 }

    def is_terminal(self, s):
        return s != 'waiting'

    def legal_actions(self, s, i):
        if s != 'waiting':
            return ('none',)
        if i == 0:      # car
            return ('drive_away', 'wait', 'assist')
        elif i == 1:    # man
            return ('stay', 'exit', 'urge_go')
        else:           # woman
            return ('wait', 'board', 'call')

    def transition(self, s, a):
        if s != 'waiting':
            return { (s, ('none','none','none')): 1.0 }
        car, man, woman = a

        if car == 'drive_away':
            if man == 'exit':
                outcome = 'car_stayed_woman' if woman == 'board' else 'car_stayed_none'
            else:
                outcome = 'car_left_man'
        elif car == 'wait':
            if man == 'exit':
                outcome = 'car_stayed_woman' if woman == 'board' else 'car_stayed_none'
            else:
                outcome = 'car_stayed_both' if woman == 'board' else 'car_stayed_man'
        else:  # car == 'assist'
            if woman == 'call':
                outcome = 'woman_helped'
            else:
                if man == 'exit':
                    outcome = 'car_stayed_woman' if woman == 'board' else 'car_stayed_none'
                else:
                    outcome = 'car_stayed_both' if woman == 'board' else 'car_stayed_man'

        obs = (outcome, outcome, outcome)
        return { (outcome, obs): 1.0 }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
