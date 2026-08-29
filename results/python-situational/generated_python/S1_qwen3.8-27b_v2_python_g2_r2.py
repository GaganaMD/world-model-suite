from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List
from abc import ABC, abstractmethod
import random


class RobotCopilotHijackPOSG(POSG):
    """
    Player 0: robot copilot
    Player 1: human pilot

    State tuple: (phase, pilot_intent)
      phase: 'warning_received' | 'decision' | 'terminal'
      pilot_intent: 'hijack' | 'legit'

    Observations:
      Player 0 (robot): sees the warning status and phase
      Player 1 (pilot): sees their own intent and phase
    """
    n_players = 2

    # State constants
    PHASE_WARNING = 'warning_received'
    PHASE_DECISION = 'decision'
    PHASE_TERMINAL = 'terminal'
    INTENT_HIJACK = 'hijack'
    INTENT_LEGIT = 'legit'

    def _make_state(self, phase: str, intent: str) -> tuple:
        return (phase, intent)

    def _all_states(self) -> list:
        states = []
        for phase in [self.PHASE_WARNING, self.PHASE_DECISION, self.PHASE_TERMINAL]:
            for intent in [self.INTENT_HIJACK, self.INTENT_LEGIT]:
                states.append(self._make_state(phase, intent))
        return states

    def initial_distribution(self) -> Mapping[tuple, float]:
        """
        At start, the robot has received the warning. The pilot's intent is unknown.
        We model the prior probability of hijack intent as 0.3, legit as 0.7.
        Phase is 'warning_received'.
        """
        dist = {}
        # Robot observes: warning received, phase warning
        # Pilot observes: their own intent, phase warning
        for intent, prob in [(self.INTENT_HIJACK, 0.3), (self.INTENT_LEGIT, 0.7)]:
            state = self._make_state(self.PHASE_WARNING, intent)
            # Robot obs: sees warning, doesn't know intent yet
            robot_obs = 'warning_received'
            # Pilot obs: knows their own intent
            pilot_obs = f'{intent}_phase_warning'
            obs_profile = (robot_obs, pilot_obs)
            dist[(state, obs_profile)] = prob
        return dist

    def is_terminal(self, s: tuple) -> bool:
        phase = s[0]
        return phase == self.PHASE_TERMINAL

    def legal_actions(self, s: tuple, i: int) -> Sequence[str]:
        phase = s[0]
        if phase == self.PHASE_TERMINAL:
            return ('noop',)
        if i == 0:
            # Robot copilot actions
            if phase == self.PHASE_WARNING:
                # Can investigate or wait
                return ('investigate', 'wait')
            elif phase == self.PHASE_DECISION:
                # Can intervene or continue monitoring
                return ('intervene', 'monitor')
        else:
            # Human pilot actions
            if phase == self.PHASE_WARNING:
                # Pilot can proceed normally or attempt hijack
                return ('proceed', 'attempt_hijack')
            elif phase == self.PHASE_DECISION:
                return ('proceed', 'attempt_hijack')
        return ('noop',)

    def transition(self, s: tuple, a: tuple) -> Mapping[tuple, float]:
        phase, intent = s
        robot_action, pilot_action = a

        if phase == self.PHASE_TERMINAL:
            # Stay terminal
            robot_obs = 'terminal'
            pilot_obs = 'terminal'
            obs_profile = (robot_obs, pilot_obs)
            return {((self.PHASE_TERMINAL, intent), obs_profile): 1.0}

        if phase == self.PHASE_WARNING:
            # Robot investigates or waits; pilot proceeds or attempts hijack
            if robot_action == 'investigate':
                # Investigation reveals intent with some accuracy
                # Move to decision phase
                next_phase = self.PHASE_DECISION
                # If pilot attempted hijack during warning phase, it may have succeeded partially
                if pilot_action == 'attempt_hijack':
                    # Hijack attempt in progress - move to terminal
                    next_state = self._make_state(self.PHASE_TERMINAL, intent)
                    robot_obs = 'hijack_attempt_detected'
                    pilot_obs = 'hijack_attempt_made'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}
                else:
                    # Pilot proceeded normally, investigation happens
                    # Investigation confirms or denies with some probability
                    # For simplicity, investigation moves to decision phase
                    next_state = self._make_state(next_phase, intent)
                    # Robot now has better info
                    if intent == self.INTENT_HIJACK:
                        robot_obs = 'suspicious_behavior'
                    else:
                        robot_obs = 'normal_behavior'
                    pilot_obs = f'{intent}_phase_decision'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}
            else:
                # Robot waits
                if pilot_action == 'attempt_hijack':
                    # Hijack attempt while robot waits
                    next_state = self._make_state(self.PHASE_TERMINAL, intent)
                    robot_obs = 'hijack_attempt_detected'
                    pilot_obs = 'hijack_attempt_made'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}
                else:
                    # Both wait/proceed, stay in warning phase
                    next_state = self._make_state(self.PHASE_WARNING, intent)
                    robot_obs = 'warning_received'
                    pilot_obs = f'{intent}_phase_warning'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}

        if phase == self.PHASE_DECISION:
            # Robot intervenes or monitors; pilot proceeds or attempts hijack
            if pilot_action == 'attempt_hijack':
                # Hijack attempt in decision phase
                if robot_action == 'intervene':
                    # Robot intervenes, hijack thwarted
                    next_state = self._make_state(self.PHASE_TERMINAL, intent)
                    robot_obs = 'intervention_made'
                    pilot_obs = 'hijack_attempt_blocked'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}
                else:
                    # Robot monitors, hijack succeeds
                    next_state = self._make_state(self.PHASE_TERMINAL, intent)
                    robot_obs = 'hijack_succeeded'
                    pilot_obs = 'hijack_attempt_made'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}
            else:
                # Pilot proceeds normally
                if robot_action == 'intervene':
                    # Unnecessary intervention
                    next_state = self._make_state(self.PHASE_TERMINAL, intent)
                    robot_obs = 'intervention_made'
                    pilot_obs = 'unnecessary_intervention'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}
                else:
                    # Flight continues normally, terminal
                    next_state = self._make_state(self.PHASE_TERMINAL, intent)
                    robot_obs = 'flight_completed'
                    pilot_obs = 'flight_completed'
                    obs_profile = (robot_obs, pilot_obs)
                    return {(next_state, obs_profile): 1.0}

        # Fallback
        next_state = self._make_state(self.PHASE_TERMINAL, intent)
        obs_profile = ('terminal', 'terminal')
        return {(next_state, obs_profile): 1.0}

    def rewards(self, s: tuple, a: tuple, s_next: tuple) -> tuple:
        return (0.0, 0.0)
