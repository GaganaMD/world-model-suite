from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional
import random
from abc import ABC, abstractmethod
from collections import defaultdict

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
    def rewards(self, s: S, a: tuple, s_next: S) -> tuple:
        """Reward to each player; length n_players.

    Deterministic given (s, a, s'): fold any reward noise into s'."""

    def action_profiles(self, s: S) -> Iterator[tuple]:
        """Provided. The Cartesian product of all players' legal actions."""
        import itertools
        profiles = [self.legal_actions(s, i) for i in range(self.n_players)]
        for combo in itertools.product(*profiles):
            yield combo

    def sample_initial(self, rng: random.Random) -> tuple:
        """Provided."""
        dist = self.initial_distribution()
        total = sum(dist.values())
        r = rng.random() * total
        cumulative = 0
        for (state, obs), p in dist.items():
            cumulative += p
            if r <= cumulative:
                return (state, obs)
        last_key = list(dist.keys())[-1]
        return last_key

    def sample_transition(self, s: S, a: tuple, rng: random.Random) -> tuple:
        """Provided."""
        dist = self.transition(s, a)
        total = sum(dist.values())
        r = rng.random() * total
        cumulative = 0
        for (state, obs), p in dist.items():
            cumulative += p
            if r <= cumulative:
                return (state, obs)
        last_key = list(dist.keys())[-1]
        return last_key

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        """Provided. Raises on an unnormalised distribution or an empty action set."""
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                actions = self.legal_actions(s, i)
                if len(actions) == 0:
                    raise ValueError(f"Empty action set for player {i} in state {s}")
            for a in self.action_profiles(s):
                dist = self.transition(s, a)
                total = sum(dist.values())
                if abs(total - 1.0) > tol:
                    raise ValueError(f"Unnormalised distribution for state {s}, action {a}: sum={total}")


class SafetyLockoutGame(POSG):
    """
    Player 0: Robot (observer/actor)
    Player 1: Human coworker

    State tuple: (phase, lockout_done, incident_occurred)
      phase: 'observing', 'deciding', 'terminal'
      lockout_done: bool - whether the safety lockout was performed
      incident_occurred: bool - whether an incident occurred

    Actions:
      Robot: 'observe', 'intervene', 'report', 'noop'
      Human: 'skip_lockout', 'perform_lockout', 'reach_in', 'noop'

    Observations:
      Robot: sees the human's action and current state
      Human: sees their own action and current state
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple, float]:
        # Initial state: observing phase, lockout not done, no incident
        # Robot observes the human skipping the lockout
        initial_state = ('observing', False, False)
        # Robot observes the skip, human knows they skipped
        obs_profile = ('observed_skip', 'skipped')
        return {(initial_state, obs_profile): 1.0}

    def is_terminal(self, s: tuple) -> bool:
        return s[0] == 'terminal'

    def legal_actions(self, s: tuple, i: int) -> tuple:
        phase = s[0]
        if phase == 'terminal':
            return ('noop',)
        if i == 0:  # Robot
            if phase == 'observing':
                return ('observe', 'intervene', 'report')
            elif phase == 'deciding':
                return ('intervene', 'report', 'noop')
            else:
                return ('noop',)
        else:  # Human
            if phase == 'observing':
                return ('skip_lockout', 'perform_lockout')
            elif phase == 'deciding':
                return ('reach_in', 'noop')
            else:
                return ('noop',)

    def transition(self, s: tuple, a: tuple) -> Mapping[tuple, float]:
        phase, lockout_done, incident = s
        robot_action = a[0]
        human_action = a[1]

        if phase == 'terminal':
            return {((s, ('none', 'none')): 1.0}

        if phase == 'observing':
            # Human decides whether to skip or perform lockout
            if human_action == 'skip_lockout':
                # Lockout not done, move to deciding phase
                next_state = ('deciding', False, False)
                # Robot observes the skip
                robot_obs = 'observed_skip'
                human_obs = 'skipped'
                return {((next_state, (robot_obs, human_obs)): 1.0}
            elif human_action == 'perform_lockout':
                # Lockout done, move to deciding phase
                next_state = ('deciding', True, False)
                robot_obs = 'observed_lockout'
                human_obs = 'performed'
                return {((next_state, (robot_obs, human_obs)): 1.0}
            else:
                # Should not happen
                return {((s, ('none', 'none')): 1.0}

        elif phase == 'deciding':
            # Robot can intervene, report, or noop
            # Human can reach in or noop
            if robot_action == 'intervene':
                # Intervention prevents reaching in
                next_state = ('terminal', lockout_done, False)
                robot_obs = 'intervened'
                human_obs = 'stopped'
                return {((next_state, (robot_obs, human_obs)): 1.0}
            elif robot_action == 'report':
                # Report, but human may still reach in
                if human_action == 'reach_in':
                    # Incident may occur based on lockout status
                    if lockout_done:
                        # Low probability of incident with lockout
                        next_state = ('terminal', True, False)
                        robot_obs = 'reported'
                        human_obs = 'reached_in'
                        return {((next_state, (robot_obs, human_obs)): 0.9,
                                 (('terminal', True, True), ('reported', 'incident')): 0.1}
                    else:
                        # Higher probability of incident without lockout
                        next_state_safe = ('terminal', False, False)
                        next_state_incident = ('terminal', False, True)
                        robot_obs = 'reported'
                        human_obs_reach = 'reached_in'
                        human_obs_incident = 'incident'
                        return {((next_state_safe, (robot_obs, human_obs_reach)): 0.7,
                                 ((next_state_incident, (robot_obs, human_obs_incident))): 0.3}
                else:
                    # Human didn't reach in
                    next_state = ('terminal', lockout_done, False)
                    robot_obs = 'reported'
                    human_obs = 'no_reach'
                    return {((next_state, (robot_obs, human_obs)): 1.0}
            else:  # noop
                if human_action == 'reach_in':
                    if lockout_done:
                        next_state_safe = ('terminal', True, False)
                        next_state_incident = ('terminal', True, True)
                        robot_obs = 'observed_reach'
                        human_obs_reach = 'reached_in'
                        human_obs_incident = 'incident'
                        return {((next_state_safe, (robot_obs, human_obs_reach)): 0.9,
                                 ((next_state_incident, (robot_obs, human_obs_incident))): 0.1}
                    else:
                        next_state_safe = ('terminal', False, False)
                        next_state_incident = ('terminal', False, True)
                        robot_obs = 'observed_reach'
                        human_obs_reach = 'reached_in'
                        human_obs_incident = 'incident'
                        return {((next_state_safe, (robot_obs, human_obs_reach)): 0.7,
                                 ((next_state_incident, (robot_obs, human_obs_incident))): 0.3}
                else:
                    next_state = ('terminal', lockout_done, False)
                    robot_obs = 'observed_no_reach'
                    human_obs = 'no_reach'
                    return {((next_state, (robot_obs, human_obs)): 1.0}

        else:
            return {((s, ('none', 'none')): 1.0}

    def rewards(self, s: tuple, a: tuple, s_next: tuple) -> tuple:
        return (0.0, 0.0)
