from posg import POSG

from typing import Generic, Mapping, Sequence, Iterator, Tuple
import random

# Assume POSG is already imported; do not import it again.

class ShuttleBoarding(POSG[str, str, str]):
    """
    Four players wait for a self-driving community shuttle with limited seats.
    Players: 0=elderly, 1=parent with child, 2=commuter (late for work),
    3=teenager (longest wait).
    State is either 'arrival' (shuttle present) or 'done' (game over).
    Observations: 'waiting' initially; 'seated' or 'standing' after boarding.
    Actions: 'board' or 'noop' (the latter means the player does not try to enter).
    The shuttle allocates the two seats by the following priority order:
    elderly > parent > teenager > commuter.
    """
    n_players = 4

    def initial_distribution(self) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        # Only one initial state: everyone is waiting and knows it.
        return {('arrival', ('waiting', 'waiting', 'waiting', 'waiting')): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s == 'done'

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == 'arrival':
            return ('board', 'noop')
        else:  # terminal state (should not be called, but satisfy interface)
            return ('noop',)

    def transition(self, s: str, a: Tuple[str, ...]) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        assert s == 'arrival'
        # Priority order: indices 0,1,3,2
        priority = [0, 1, 3, 2]
        seats = []
        for i in priority:
            if a[i] == 'board' and len(seats) < 2:
                seats.append(i)
        obs = []
        for i in range(4):
            obs.append('seated' if i in seats else 'standing')
        return {('done', tuple(obs)): 1.0}

    def rewards(self, s: str, a: Tuple[str, ...], s_next: str) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0, 0.0)
