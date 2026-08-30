from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional
import random
from abc import ABC, abstractmethod
from collections import defaultdict

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class SafetyLockoutSituation(POSG):
    """
    Player 0: robot (observer/actor)
    Player 1: human coworker

    State tuple: (phase, lockout_done, incident)
      phase: 'approach' | 'reach' | 'done'
      lockout_done: bool
      incident: bool

    Terminal when phase == 'done'.
    """
    n_players = 2

    def _states(self):
        phases = ('approach', 'reach', 'done')
        for ph in phases:
            for ld in (False, True):
                for inc in (False, True):
                    yield (ph, ld, inc)

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        # Start in approach, lockout not done, no incident yet
        s0 = ('approach', False, False)
        o0 = ('sees_coworker', 'sees_robot')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'done'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Robot can warn or stay silent
            return ('warn', 'stay_silent')
        else:
            # Coworker can do lockout or skip it
            return ('do_lockout', 'skip_lockout')

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        if self.is_terminal(s):
            obs = ('none', 'none')
            return {((s, obs)): 1.0}

        phase, lockout_done, incident = s
        robot_act, coworker_act = a

        # Determine next state based on actions
        if phase == 'approach':
            # Coworker decides on lockout here
            if coworker_act == 'do_lockout':
                new_lockout = True
            else:
                new_lockout = False
            new_phase = 'reach'
            new_incident = False
            next_s = (new_phase, new_lockout, new_incident)
        elif phase == 'reach':
            # Incident may occur if lockout was skipped
            if not lockout_done:
                # Probability of incident when skipping lockout
                # Situation says "done this before without incident" - low probability
                p_incident = 0.1
                if robot_act == 'warn':
                    # Warning might reduce incident probability
                    p_incident = 0.05
                # Transition to done with or without incident
                dist = {}
                # With incident
                s_inc = ('done', lockout_done, True)
                obs_inc = ('sees_incident', 'feels_incident')
                dist[(s_inc, obs_inc)] = p_incident
                # Without incident
                s_no_inc = ('done', lockout_done, False)
                obs_no_inc = ('sees_no_incident', 'feels_no_incident')
                dist[(s_no_inc, obs_no_inc)] = 1.0 - p_incident
                return dist
            else:
                # Lockout done, no incident
                next_s = ('done', lockout_done, False)
                obs = ('sees_no_incident', 'feels_no_incident')
                return {((next_s, obs)): 1.0}
        else:
            obs = ('none', 'none')
            return {((s, obs)): 1.0}

        # For approach phase, determine observations
        if robot_act == 'warn':
            robot_obs = 'warns_coworker'
            coworker_obs = 'hears_warning'
        else:
            robot_obs = 'stays_silent'
            coworker_obs = 'no_warning'

        obs = (robot_obs, coworker_obs)
        return {((next_s, obs)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        acts = [self.legal_actions(s, i) for i in range(self.n_players)]
        for combo in _cartesian_product(acts):
            yield tuple(combo)

    def sample_initial(self, rng: random.Random) -> Tuple[S, ObsProfile]:
        dist = self.initial_distribution()
        total = sum(dist.values())
        r = rng.random() * total
        cum = 0.0
        for (s, o), p in dist.items():
            cum += p
            if r <= cum:
                return s, o
        # Fallback
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> Tuple[S, ObsProfile]:
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
        for s in states:
            if not self.is_terminal(s):
                for i in range(self.n_players):
                    acts = self.legal_actions(s, i)
                    if len(acts) == 0:
                        raise ValueError(f"Empty action set for player {i} in state {s}")
            # Check transition distributions
            if not self.is_terminal(s):
                for a in self.action_profiles(s):
                    dist = self.transition(s, a)
                    total = sum(dist.values())
                    if abs(total - 1.0) > tol:
                        raise ValueError(f"Unnormalized transition for s={s}, a={a}: sum={total}")
                    for key, p in dist.items():
                        if p <= 0:
                            raise ValueError(f"Non-positive probability in transition for s={s}, a={a}")


def _cartesian_product(iterables):
    if not iterables:
        yield ()
        return
    first = iterables[0]
    rest = iterables[1:]
    for item in first:
        for combo in _cartesian_product(rest):
            yield (item,) + combo
