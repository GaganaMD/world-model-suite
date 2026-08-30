from posg import POSG

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Mapping, Sequence, Iterator, Tuple, Dict, List, Any

S = TypeVar('S')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class POSG(ABC, Generic[S, O]):
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
    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        """P(s_0, o_0).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        """..."""

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        """Actions available to player i in state s.  Non-empty."""

    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        """P(s', o | s, a).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        """Reward to each player; length n_players.

Deterministic given (s, a, s'): fold any reward noise into s'."""

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        """Provided. The Cartesian product of all players' legal actions."""
        import itertools
        profiles = [self.legal_actions(s, i) for i in range(self.n_players)]
        for combo in itertools.product(*profiles):
            yield combo

    def sample_initial(self, rng: random.Random) -> Tuple[S, ObsProfile]:
        """Provided."""
        import random
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

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> Tuple[S, ObsProfile]:
        """Provided."""
        import random
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

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if len(acts) == 0:
                    raise ValueError(f"Empty action set for player {i} in state {s}")
            for a in self.action_profiles(s):
                dist = self.transition(s, a)
                total = sum(dist.values())
                if abs(total - 1.0) > tol:
                    raise ValueError(f"Unnormalised transition for state {s}, action {a}: sum={total}")


class HijackWarningPOSG(POSG):
    """
    Player 0: Robot copilot
    Player 1: Human pilot

    State tuple: (warning_status, copilot_action_taken, pilot_action_taken)
      - warning_status: 'unconfirmed' or 'confirmed'
      - copilot_action_taken: 'none' or 'alerted'
      - pilot_action_taken: 'none' or 'hijacked'

    Terminal when either copilot has alerted or pilot has hijacked.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        # Initial state: warning unconfirmed, no actions taken yet
        # Copilot observes the warning; pilot observes nothing special
        return {
            (('unconfirmed', 'none', 'none'), ('warning_received', 'none')): 1.0
        }

    def is_terminal(self, s: S) -> bool:
        _, copilot_action, pilot_action = s
        return copilot_action == 'alerted' or pilot_action == 'hijacked'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Copilot can alert or wait
            return ('alert', 'wait')
        else:
            # Pilot can hijack or wait
            return ('hijack', 'wait')

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        warning_status, copilot_action, pilot_action = s
        copilot_act, pilot_act = a

        if self.is_terminal(s):
            return {((s, ('none', 'none')), 1.0)}

        new_copilot_action = copilot_action
        new_pilot_action = pilot_action

        if copilot_act == 'alert':
            new_copilot_action = 'alerted'
        if pilot_act == 'hijack':
            new_pilot_action = 'hijacked'

        new_state = (warning_status, new_copilot_action, new_pilot_action)

        # Observations
        # Copilot sees if they alerted or if pilot hijacked
        # Pilot sees if they hijacked or if copilot alerted
        if new_copilot_action == 'alerted':
            copilot_obs = 'alert_sent'
        elif new_pilot_action == 'hijacked':
            copilot_obs = 'hijack_detected'
        else:
            copilot_obs = 'none'

        if new_pilot_action == 'hijacked':
            pilot_obs = 'hijack_executed'
        elif new_copilot_action == 'alerted':
            pilot_obs = 'alert_received'
        else:
            pilot_obs = 'none'

        obs_profile = (copilot_obs, pilot_obs)

        return {((new_state, obs_profile), 1.0)}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
