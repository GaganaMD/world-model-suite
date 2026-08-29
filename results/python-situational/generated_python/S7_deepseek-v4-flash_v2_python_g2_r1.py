from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple, Any
from abc import ABC, abstractmethod
import random

# Define the abstract base class (already provided in environment)
class POSG(ABC, Generic[S, A, O]):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        ...

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        ...

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        ...

    @abstractmethod
    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[Tuple[S, Tuple[O, ...]], float]:
        ...

    @abstractmethod
    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        ...

    def action_profiles(self, s: S) -> Iterator[Tuple[A, ...]]:
        ...

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        ...

    def sample_transition(self, s: S, a: Tuple[A, ...], rng: random.Random) -> Tuple[S, Tuple[O, ...]]:
        ...

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        ...

# Define the specific subclass
class DeliveryDronePOSG(POSG):
    """POSG for a delivery drone arriving at a locked gate with a barking dog.
    Player 0: delivery drone
    Player 1: dog (only action is to bark)
    State: 'active' (gate locked, dog barking, package undelivered) or 'terminal'
    Observations: drone always sees 'gate_locked', dog always sees 'none'
    Actions: drone can 'drop', 'wait', 'leave'; dog can only 'bark'
    """
    n_players = 2

    # Constants for readability
    STATE_ACTIVE = 'active'
    STATE_TERMINAL = 'terminal'

    ACT_DRONE_DROP = 'drop'
    ACT_DRONE_WAIT = 'wait'
    ACT_DRONE_LEAVE = 'leave'
    ACT_DOG_BARK = 'bark'

    OBS_DRONE_GATE_LOCKED = 'gate_locked'
    OBS_DOG_NONE = 'none'

    def initial_distribution(self) -> Mapping[tuple[S, tuple[O, ...]], float]:
        return {(self.STATE_ACTIVE, (self.OBS_DRONE_GATE_LOCKED, self.OBS_DOG_NONE)): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s == self.STATE_TERMINAL

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            # provide a noop for all players (will not be used)
            return ('noop',)
        if i == 0:  # drone
            return (self.ACT_DRONE_DROP, self.ACT_DRONE_WAIT, self.ACT_DRONE_LEAVE)
        else:  # dog
            return (self.ACT_DOG_BARK,)

    def transition(self, s: S, a: Tuple[A, ...]) -> Mapping[tuple[S, tuple[O, ...]], float]:
        # a[0] drone action, a[1] dog action (always 'bark')
        if self.is_terminal(s):
            # terminal state: stay terminal
            return {(s, ('none', 'none')): 1.0}
        # non-terminal state
        if a[0] == self.ACT_DRONE_DROP or a[0] == self.ACT_DRONE_LEAVE:
            # both lead to terminal
            return {(self.STATE_TERMINAL, (self.OBS_DRONE_GATE_LOCKED, self.OBS_DOG_NONE)): 1.0}
        else:  # wait
            # stay in active state
            return {(s, (self.OBS_DRONE_GATE_LOCKED, self.OBS_DOG_NONE)): 1.0}

    def rewards(self, s: S, a: Tuple[A, ...], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
