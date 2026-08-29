from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict

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

    def sample_initial(self, rng: random.Random) -> tuple[S, ObsProfile]:
        """Provided."""

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> tuple[S, ObsProfile]:
        """Provided."""

    def validate(self, states: Sequence[S], tol: float=1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
