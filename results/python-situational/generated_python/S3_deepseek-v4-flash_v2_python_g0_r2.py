from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# Type aliases for clarity
S = str
A = str
O = str

class CarPOSG(POSG[S, A, O]):
    """Two players: man (index 0) and pregnant woman (index 1).
    State is one of:
        'initial'   – man inside, woman outside, car waiting
        'departed'  – car has driven away (man inside, woman outside)
        'both_inside' – woman has boarded, car still waiting
    Observations are the same string for both players.
    """

    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        return {("initial", ("initial", "initial")): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s in ("departed", "both_inside")

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:  # man
            return ("depart", "wait")
        else:       # woman
            return ("board", "stay")

    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        man_act, woman_act = a
        if s != "initial":
            # Terminal state – only noop actions, stay in same state
            return {(s, (s, s)): 1.0}

        if man_act == "depart":
            # Car leaves regardless of woman's action
            next_s = "departed"
        else:  # man waits
            if woman_act == "board":
                next_s = "both_inside"
            else:  # woman stays
                next_s = "initial"

        obs = (next_s, next_s)
        return {(next_s, obs): 1.0}

    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
