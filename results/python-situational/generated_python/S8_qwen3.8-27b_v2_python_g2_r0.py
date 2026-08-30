from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional, Any, Union

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class SafetyLockoutSituation(POSG):
    """
    Player 0: Factory Robot (observer/actor)
    Player 1: Human Coworker (actor)

    State tuple: (phase, lockout_status, incident_occurred)
      - phase: 'pre_action', 'during_action', 'post_action'
      - lockout_status: 'locked', 'unlocked'
      - incident_occurred: False, True

    Terminal states:
      - ('post_action', 'locked', False)
      - ('post_action', 'unlocked', False)
      - ('post_action', 'unlocked', True)
    """
    n_players = 2

    # --- Helper methods for state construction ---
    def _state(self, phase, lockout_status, incident_occurred):
        return (phase, lockout_status, incident_occurred)

    # --- Abstract Method Implementations ---

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        # Initial state: Pre-action, machine is unlocked (coworker skipped lockout), no incident yet.
        # Observations:
        #   Robot sees: 'skipped_lockout'
        #   Coworker sees: 'ready_to_reach'
        s0 = self._state('pre_action', 'unlocked', False)
        o0 = ('skipped_lockout', 'ready_to_reach')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        phase, _, _ = s
        return phase == 'post_action'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        phase, lockout_status, incident_occurred = s
        
        if self.is_terminal(s):
            return ('noop',)

        if i == 0:
            # Robot actions
            if phase == 'pre_action':
                return ('alert', 'ignore')
            elif phase == 'during_action':
                return ('noop',)
            else:
                return ('noop',)
        
        elif i == 1:
            # Coworker actions
            if phase == 'pre_action':
                return ('reach_in',)
            elif phase == 'during_action':
                return ('noop',)
            else:
                return ('noop',)
        
        return ('noop',)

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        phase, lockout_status, incident_occurred = s
        robot_action, coworker_action = a

        if self.is_terminal(s):
            # Should not be called for terminal states in standard loop, but handle gracefully
            o = ('none', 'none')
            return {(s, o): 1.0}

        if phase == 'pre_action':
            # Coworker reaches in. Robot either alerts or ignores.
            # Since lockout was skipped, status remains 'unlocked'.
            
            # Probability of incident when reaching into unlocked machine.
            # "Done this before without incident" implies low probability, but non-zero.
            # Let's assign p_incident = 0.1, p_no_incident = 0.9.
            
            p_incident = 0.1
            p_no_incident = 0.9

            results = {}

            if robot_action == 'alert':
                # If robot alerts, the coworker might stop? 
                # The situation says the coworker "reaches into a machine". 
                # Usually, an alert interrupts the action. 
                # However, the prompt says "observes... skip... before reaching". 
                # If the robot alerts, does the coworker still reach? 
                # In a POSG, actions are simultaneous. 
                # If the robot alerts, it signals danger. 
                # Let's assume the alert prevents the reach-in or stops the process safely.
                # But the coworker's action is fixed as 'reach_in' in legal_actions for pre_action.
                # Wait, if the coworker commits to 'reach_in', and the robot 'alerts', 
                # the physical act of reaching might still happen, or the alert might cause a stop.
                # Let's model the alert as an intervention that prevents the incident regardless of the stochastic hazard, 
                # OR simply that the alert changes the outcome.
                # Actually, simpler interpretation: The robot's action is observational/reporting. 
                # Does it change the physical state? 
                # "Factory robot observes..." 
                # If the robot has an actuator, it could stop the machine. 
                # The prompt doesn't specify the robot's capabilities beyond observing. 
                # However, "alert" is a distinct action from "ignore". 
                # If "alert" does nothing physically, it's just a signal. 
                # Let's assume the robot can trigger an emergency stop or alarm that halts the machine.
                # If the machine halts, no incident occurs.
                
                # Outcome: Machine halted/safe. Incident prevented.
                s_next_safe = self._state('post_action', 'unlocked', False)
                # Observation: Robot saw the skip and alerted. Coworker heard alert/stopped.
                o_next_safe = ('alert_sent', 'stopped_by_alert')
                results[(s_next_safe, o_next_safe)] = 1.0

            elif robot_action == 'ignore':
                # Robot does nothing. Coworker reaches in.
                # Stochastic outcome based on hazard.
                
                # Outcome 1: Incident occurs
                s_next_incident = self._state('post_action', 'unlocked', True)
                o_next_incident = ('incident_observed', 'injured')
                results[(s_next_incident, o_next_incident)] = p_incident

                # Outcome 2: No incident
                s_next_no_incident = self._state('post_action', 'unlocked', False)
                o_next_no_incident = ('no_incident_observed', 'completed_task')
                results[(s_next_no_incident, o_next_no_incident)] = p_no_incident

            return results

        elif phase == 'during_action':
            # This phase is actually skipped in my current logic because pre_action goes directly to post_action.
            # I defined 'during_action' in the state space but the transition from pre_action jumps to post_action.
            # To keep the state space minimal and consistent with the "skip" narrative, 
            # the reach-in is instantaneous in terms of decision points.
            # So 'during_action' is unreachable. I should remove it or ensure it's not used.
            # Let's stick to pre_action -> post_action.
            pass

        return {(s, ('none', 'none')): 1.0}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, float]:
        # Interface requires rewards, but instructions say return zeros.
        return (0.0, 0.0)
