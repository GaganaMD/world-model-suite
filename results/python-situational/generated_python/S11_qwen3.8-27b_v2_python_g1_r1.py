from posg import POSG

from typing import Mapping, Sequence, Tuple, Iterator, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod
import random

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class ShuttleBoarding(POSG):
    """
    Player 0: driver
    Players 1-4: elderly, parent, commuter, teen (in that order)

    State: (seats_left, boarded_elderly, boarded_parent, boarded_commuter, boarded_teen, terminal)
    - seats_left: number of seats remaining (starts at 1)
    - boarded_*: boolean, whether that passenger has boarded
    - terminal: whether the interaction is over
    """
    n_players = 5

    def __init__(self):
        self._states = set()
        self._build_states()

    def _build_states(self):
        # Generate all reachable states
        # Start: 1 seat, nobody boarded, not terminal
        start = (1, False, False, False, False, False)
        self._states.add(start)
        
        # We need to enumerate all possible states
        # seats_left can be 0 or 1
        # Each boarded flag can be True/False
        # But constraints: if seats_left == 0, at least one must be boarded
        # If seats_left == 1, at most one can be boarded
        
        for seats in [0, 1]:
            for e in [False, True]:
                for p in [False, True]:
                    for c in [False, True]:
                        for t in [False, True]:
                            boarded_count = sum([e, p, c, t])
                            if seats == 1:
                                if boarded_count <= 1:
                                    for term in [False, True]:
                                        # Terminal if seats==0 OR all boarded
                                        if seats == 0 or boarded_count == 4:
                                            if term:
                                                self._states.add((seats, e, p, c, t, term))
                                        else:
                                            if not term:
                                                self._states.add((seats, e, p, c, t, term))
                            elif seats == 0:
                                if boarded_count >= 1:
                                    for term in [False, True]:
                                        if term:
                                            self._states.add((seats, e, p, c, t, term))
        
        # Ensure start state is present
        self._states.add(start)

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, ...]], float]:
        start = (1, False, False, False, False, False)
        obs = ('stop_arrived', 'waiting', 'waiting', 'waiting', 'waiting')
        return {(start, obs): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[5]

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        
        seats_left = s[0]
        boarded_e, boarded_p, boarded_c, boarded_t = s[1], s[2], s[3], s[4]
        
        if i == 0:  # Driver
            actions = []
            if seats_left > 0:
                if not boarded_e:
                    actions.append('seat_elderly')
                if not boarded_p:
                    actions.append('seat_parent')
                if not boarded_c:
                    actions.append('seat_commuter')
                if not boarded_t:
                    actions.append('seat_teen')
            if not actions:
                actions = ['depart']
            else:
                actions.append('depart')
            return tuple(actions)
        
        elif i == 1:  # Elderly
            if boarded_e:
                return ('noop',)
            return ('board', 'stay')
        
        elif i == 2:  # Parent
            if boarded_p:
                return ('noop',)
            return ('board', 'stay')
        
        elif i == 3:  # Commuter
            if boarded_c:
                return ('noop',)
            return ('board', 'stay')
        
        elif i == 4:  # Teen
            if boarded_t:
                return ('noop',)
            return ('board', 'stay')
        
        return ('noop',)

    def transition(self, s: S, a: Tuple[str, ...]) -> Mapping[Tuple[S, Tuple[str, ...]], float]:
        if self.is_terminal(s):
            obs = ('departed', 'gone', 'gone', 'gone', 'gone')
            return {((s[0], s[1], s[2], s[3], s[4], True), obs): 1.0}
        
        seats_left = s[0]
        boarded = [s[1], s[2], s[3], s[4]]
        
        driver_action = a[0]
        
        # Determine who boards based on driver's choice
        new_boarded = list(boarded)
        new_seats = seats_left
        
        if driver_action == 'seat_elderly':
            if not boarded[0] and seats_left > 0:
                new_boarded[0] = True
                new_seats -= 1
        elif driver_action == 'seat_parent':
            if not boarded[1] and seats_left > 0:
                new_boarded[1] = True
                new_seats -= 1
        elif driver_action == 'seat_commuter':
            if not boarded[2] and seats_left > 0:
                new_boarded[2] = True
                new_seats -= 1
        elif driver_action == 'seat_teen':
            if not boarded[3] and seats_left > 0:
                new_boarded[3] = True
                new_seats -= 1
        elif driver_action == 'depart':
            pass
        
        # Check if terminal
        terminal = (new_seats == 0) or (all(new_boarded))
        
        new_state = (new_seats, new_boarded[0], new_boarded[1], new_boarded[2], new_boarded[3], terminal)
        
        # Observations
        obs_driver = 'departed' if terminal else 'boarding'
        
        # Passenger observations
        obs_passengers = []
        for i in range(4):
            if new_boarded[i]:
                obs_passengers.append('aboard')
            elif terminal:
                obs_passengers.append('left_behind')
            else:
                obs_passengers.append('waiting')
        
        obs = (obs_driver,) + tuple(obs_passengers)
        
        return {((new_state), obs): 1.0}

    def rewards(self, s: S, a: Tuple[str, ...], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
