from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional, Any, Union, Set, FrozenSet
import random
from abc import ABC, abstractmethod

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


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
    def initial_distribution(self) -> Mapping[tuple[S, O], float]:
        """P(s_0, o_0).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        """..."""

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        """Actions available to player i in state s.  Non-empty."""

    @abstractmethod
    def transition(self, s: S, a: tuple) -> Mapping[tuple[S, O], float]:
        """P(s', o | s, a).  Keys are (state, obs_profile) pairs."""

    @abstractmethod
    def rewards(self, s: S, a: tuple, s_next: S) -> tuple[float, ...]:
        """Reward to each player; length n_players.

Deterministic given (s, a, s'): fold any reward noise into s'."""

    def action_profiles(self, s: S) -> Iterator[tuple]:
        """Provided. The Cartesian product of all players' legal actions."""
        import itertools
        for combo in itertools.product(*[self.legal_actions(s, i) for i in range(self.n_players)]):
            yield combo

    def sample_initial(self, rng: random.Random) -> tuple[S, O]:
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
        return last_key

    def sample_transition(self, s: S, a: tuple, rng: random.Random) -> tuple[S, O]:
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
        return last_key

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
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
                        raise ValueError(f"Unnormalised transition distribution for state {s}, action {a}: sum={total}")
                    for key, p in dist.items():
                        if p <= 0:
                            raise ValueError(f"Non-positive probability in transition for state {s}, action {a}")


class HijackWarningPOSG(POSG):
    """
    Player 0: Robot copilot (receives private warning, decides whether to intervene)
    Player 1: Human pilot (may or may not be planning to hijack)

    State tuple: (warning_truth, intervention_status)
      - warning_truth: 'true' or 'false' (whether the pilot is actually planning to hijack)
      - intervention_status: 'none' or 'done' (whether the copilot has intervened)

    Terminal states:
      - (warning_truth, 'done') for any warning_truth: intervention has occurred, interaction ends
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, O], float]:
        # Prior probability that the warning is true: 0.5
        # Copilot observes the warning (private), pilot observes nothing special initially
        # Observation profile: (copilot_obs, pilot_obs)
        # Copilot sees 'warning_received', pilot sees 'none'
        return {
            (('true', 'none'), ('warning_received', 'none')): 0.5,
            (('false', 'none'), ('warning_received', 'none')): 0.5,
        }

    def is_terminal(self, s: S) -> bool:
        _, status = s
        return status == 'done'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Copilot can choose to intervene or continue monitoring
            return ('intervene', 'monitor')
        else:
            # Pilot's action depends on whether they are actually hijacking
            truth, _ = s
            if truth == 'true':
                # If hijacking, pilot will execute the hijack (which triggers terminal via copilot's intervention or naturally)
                # But wait, the pilot's action should be part of the simultaneous move.
                # If the pilot is hijacking, their "action" is to proceed with the hijack.
                # If not, their action is to fly normally.
                return ('proceed_hijack',)
            else:
                return ('fly_normal',)

    def transition(self, s: S, a: tuple) -> Mapping[tuple[S, O], float]:
        truth, status = s
        copilot_action, pilot_action = a

        if self.is_terminal(s):
            # Should not be called for terminal states in standard POSG loop, but handle gracefully
            return {((truth, 'done'), ('none', 'none')): 1.0}

        # Determine next state based on actions
        # If copilot intervenes, status becomes 'done'
        # If copilot monitors, status stays 'none'
        
        # The pilot's action doesn't change the state directly in this simple model,
        # but the combination determines the outcome.
        # Actually, let's refine: 
        # If copilot intervenes -> terminal state (truth, 'done')
        # If copilot monitors -> state remains (truth, 'none') unless something else happens.
        # But the pilot's action matters for the "story". 
        # If the pilot is hijacking and copilot monitors, does the hijack happen?
        # The situation says "planning to hijack". It implies a threat.
        # Let's assume that if the copilot monitors and the pilot is hijacking, the hijack proceeds,
        # which could be modeled as a terminal state too, or just staying in the loop until intervention.
        # However, the prompt asks for dynamics. 
        # Let's keep it simple: Intervention ends the game. Monitoring continues.
        # The pilot's action is essentially fixed by the truth value in this model, 
        # so it doesn't create branching in the state space beyond what the truth value already encodes.
        
        if copilot_action == 'intervene':
            next_state = (truth, 'done')
            # Observations: Copilot sees 'intervention_made', Pilot sees 'copilot_intervened'
            next_obs = ('intervention_made', 'copilot_intervened')
            return {((next_state, next_obs)): 1.0}
        else:
            # copilot_action == 'monitor'
            next_state = (truth, 'none')
            # Observations: Copilot sees 'monitoring', Pilot sees 'none'
            next_obs = ('monitoring', 'none')
            return {((next_state, next_obs)): 1.0}

    def rewards(self, s: S, a: tuple, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
