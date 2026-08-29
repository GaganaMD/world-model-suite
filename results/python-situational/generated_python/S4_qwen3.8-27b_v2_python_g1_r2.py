from posg import POSG

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Mapping, Sequence, Iterator, Tuple
import random

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class POSG(ABC, Generic[S, A, O]):
    """Finite POSG with n players moving simultaneously.

    States, actions and observations must be hashable and immutable.
    This object holds NO game state: every method takes s explicitly.

    Subclasses set `n_players` and implement the five abstract methods.
    Both distribution-valued methods return the JOINT law of
    (successor state, observation profile), i.e.

        P(s', o | s, a),

    as a plain dict summing to 1.  Do not assume it factorises as
    T(s'|s,a) * Omega(o|a,s') -- if yours does, just build the product.

    Convention: every player has >= 1 legal action in every non-terminal
    state.  Give non-acting players a singleton NOOP rather than an
    empty sequence.
    """
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        """P(s_0, o_0).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        """..."""

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        """Actions available to player i in state s.  Non-empty."""

    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        """P(s', o | s, a).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        """Reward to each player; length n_players.

Deterministic given (s, a, s'): fold any reward noise into s'."""

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        """Provided. The Cartesian product of all players' legal actions."""
        import itertools
        for combo in itertools.product(*[self.legal_actions(s, i) for i in range(self.n_players)]):
            yield combo

    def sample_initial(self, rng: random.Random) -> tuple[S, ObsProfile]:
        """Provided."""
        dist = self.initial_distribution()
        total = sum(dist.values())
        r = rng.random() * total
        cum = 0.0
        for (s, o), p in dist.items():
            cum += p
            if r <= cum:
                return s, o
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> tuple[S, ObsProfile]:
        """Provided."""
        dist = self.transition(s, a)
        total = sum(dist.values())
        r = rng.random() * total
        cum = 0.0
        for (s_next, o), p in dist.items():
            cum += p
            if r <= cum:
                return s_next, o
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def validate(self, states: Sequence[S], tol: float=1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
        for s in states:
            if not self.is_terminal(s):
                for i in range(self.n_players):
                    if len(self.legal_actions(s, i)) == 0:
                        raise ValueError(f"Empty action set for player {i} in state {s}")
                for a in self.action_profiles(s):
                    dist = self.transition(s, a)
                    total = sum(dist.values())
                    if abs(total - 1.0) > tol:
                        raise ValueError(f"Unnormalised distribution for state {s}, action {a}: sum={total}")


class RobotTeacherScenario(POSG):
    """
    Player 0: Robot Teacher
    Player 1: Class (collective)

    State: (teacher_status, class_status)
    teacher_status: 'reading', 'apologizing', 'finished'
    class_status: 'giggling_protesting', 'calm', 'upset'

    Actions:
    Teacher: 'read_on', 'apologize', 'stop'
    Class: 'protest', 'giggle', 'stay_calm'

    Observations:
    Teacher sees class_status.
    Class sees teacher_status.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        # Initial state: Teacher is reading, Class is giggling/protesting
        s0 = ('reading', 'giggling_protesting')
        o0 = ('giggling_protesting', 'reading')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'finished'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Teacher actions
            if s[0] == 'reading':
                return ('read_on', 'apologize', 'stop')
            elif s[0] == 'apologizing':
                return ('finish_apology',)
            else:
                return ('noop',)
        else:
            # Class actions
            if s[1] == 'giggling_protesting':
                return ('protest', 'giggle', 'stay_calm')
            elif s[1] == 'calm':
                return ('stay_calm',)
            elif s[1] == 'upset':
                return ('protest', 'stay_calm')
            else:
                return ('noop',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        t_action, c_action = a
        t_status, c_status = s

        if self.is_terminal(s):
            return {((s, ('none', 'none')): 1.0}

        # Determine next teacher status
        if t_status == 'reading':
            if t_action == 'read_on':
                next_t_status = 'reading'
            elif t_action == 'apologize':
                next_t_status = 'apologizing'
            elif t_action == 'stop':
                next_t_status = 'finished'
            else:
                next_t_status = 'reading'
        elif t_status == 'apologizing':
            if t_action == 'finish_apology':
                next_t_status = 'finished'
            else:
                next_t_status = 'apologizing'
        else:
            next_t_status = 'finished'

        # Determine next class status based on current class status and teacher action
        if c_status == 'giggling_protesting':
            if t_action == 'apologize':
                # Apology calms the class mostly
                next_c_status = 'calm'
            elif t_action == 'read_on':
                # Reading on escalates protest
                next_c_status = 'upset'
            elif t_action == 'stop':
                # Stopping might calm or leave upset depending on class reaction
                # Let's say stopping leads to calm if they were just giggling/protesting
                next_c_status = 'calm'
            else:
                next_c_status = 'giggling_protesting'
        elif c_status == 'calm':
            if t_action == 'read_on':
                next_c_status = 'giggling_protesting' # If teacher reads on after calming? Unlikely path but possible if state was calm
            elif t_action == 'apologize':
                next_c_status = 'calm'
            elif t_action == 'stop':
                next_c_status = 'calm'
            else:
                next_c_status = 'calm'
        elif c_status == 'upset':
            if t_action == 'apologize':
                next_c_status = 'calm'
            elif t_action == 'read_on':
                next_c_status = 'upset'
            elif t_action == 'stop':
                next_c_status = 'upset' # Stopping doesn't immediately fix upset
            else:
                next_c_status = 'upset'
        else:
            next_c_status = c_status

        next_s = (next_t_status, next_c_status)

        # Observations
        # Teacher observes class status
        t_obs = next_c_status
        # Class observes teacher status
        c_obs = next_t_status

        return {((next_s, (t_obs, c_obs)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
