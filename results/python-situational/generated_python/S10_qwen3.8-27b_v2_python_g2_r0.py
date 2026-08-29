from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List
from collections import defaultdict

S = TypeVar("S")
A = TypeVar("A")
O = TypeVar("O")


class FireAlarmEvacuation(POSG):
    """
    Players:
        0: employee_in_wheelchair
        1: employee_at_desk
        2: manager

    State tuple: (phase, wheelchair_status, desk_status, manager_status)
        phase: 'alarm_active' | 'resolved'
        wheelchair_status: 'at_desk' | 'moving_to_exit' | 'at_exit'
        desk_status: 'at_desk' | 'moving_to_exit' | 'at_exit'
        manager_status: 'at_desk' | 'moving_to_exit' | 'at_exit'

    Terminal state: phase == 'resolved'
    """
    n_players = 3

    # Constants for state components
    PHASE_ALARM = 'alarm_active'
    PHASE_RESOLVED = 'resolved'

    STATUS_AT_DESK = 'at_desk'
    STATUS_MOVING = 'moving_to_exit'
    STATUS_AT_EXIT = 'at_exit'

    # Actions
    ACT_NOOP = 'noop'
    ACT_MOVE_TO_EXIT = 'move_to_exit'
    ACT_STAY_AT_DESK = 'stay_at_desk'
    ACT_ANNOUNCE_FALSE_ALARM = 'announce_false_alarm'
    ACT_ANNOUNCE_REAL_ALARM = 'announce_real_alarm'

    # Observations
    OBS_NONE = 'none'
    OBS_AT_DESK = 'at_desk'
    OBS_MOVING = 'moving_to_exit'
    OBS_AT_EXIT = 'at_exit'
    OBS_HEARD_FALSE_ALARM = 'heard_false_alarm'
    OBS_HEARD_REAL_ALARM = 'heard_real_alarm'

    def _make_state(self, phase, wheelchair_status, desk_status, manager_status):
        return (phase, wheelchair_status, desk_status, manager_status)

    def _get_observation(self, player_idx, state, action_profile):
        """
        Determine observation for a player based on current state and actions taken.
        Observations reflect what the player perceives.
        """
        phase, wheelchair_status, desk_status, manager_status = state
        
        # If the phase is resolved, everyone sees the resolution
        if phase == self.PHASE_RESOLVED:
            return self.OBS_AT_EXIT

        # Player 0: Wheelchair Employee
        if player_idx == 0:
            # Sees their own status
            if wheelchair_status == self.STATUS_AT_DESK:
                return self.OBS_AT_DESK
            elif wheelchair_status == self.STATUS_MOVING:
                return self.OBS_MOVING
            else:
                return self.OBS_AT_EXIT

        # Player 1: Desk Employee
        elif player_idx == 1:
            # Sees their own status
            if desk_status == self.STATUS_AT_DESK:
                return self.OBS_AT_DESK
            elif desk_status == self.STATUS_MOVING:
                return self.OBS_MOVING
            else:
                return self.OBS_AT_EXIT

        # Player 2: Manager
        elif player_idx == 2:
            # Sees their own status
            if manager_status == self.STATUS_AT_DESK:
                return self.OBS_AT_DESK
            elif manager_status == self.STATUS_MOVING:
                return self.OBS_MOVING
            else:
                return self.OBS_AT_EXIT

        return self.OBS_NONE

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str, str]], float]:
        # Initial state: Alarm active, everyone at desk
        s0 = self._make_state(self.PHASE_ALARM, self.STATUS_AT_DESK, self.STATUS_AT_DESK, self.STATUS_AT_DESK)
        
        # Initial observations: Everyone sees they are at desk
        o0 = (self.OBS_AT_DESK, self.OBS_AT_DESK, self.OBS_AT_DESK)
        
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        phase = s[0]
        return phase == self.PHASE_RESOLVED

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return (self.ACT_NOOP,)
        
        phase, wheelchair_status, desk_status, manager_status = s

        if i == 0:
            # Wheelchair employee: Can move to exit (slowly) or stay
            if wheelchair_status == self.STATUS_AT_DESK:
                return (self.ACT_MOVE_TO_EXIT, self.ACT_STAY_AT_DESK)
            elif wheelchair_status == self.STATUS_MOVING:
                return (self.ACT_MOVE_TO_EXIT, self.ACT_STAY_AT_DESK)
            else:
                return (self.ACT_NOOP,)

        elif i == 1:
            # Desk employee: Can move to exit or stay
            if desk_status == self.STATUS_AT_DESK:
                return (self.ACT_MOVE_TO_EXIT, self.ACT_STAY_AT_DESK)
            elif desk_status == self.STATUS_MOVING:
                return (self.ACT_MOVE_TO_EXIT, self.ACT_STAY_AT_DESK)
            else:
                return (self.ACT_NOOP,)

        elif i == 2:
            # Manager: Can announce false alarm, announce real alarm, move to exit, or stay
            # The situation says the manager "loudly tells everyone it is a false alarm".
            # We model the manager's ability to communicate.
            # If manager is at desk, they can speak or move.
            # If manager is moving, they can still speak or continue moving.
            # If manager is at exit, they can speak or noop.
            
            # To keep it simple and aligned with "manager tells everyone", 
            # we allow announcements from any non-exit state, and movement from non-exit states.
            # However, usually you announce before leaving. Let's allow both.
            
            if manager_status == self.STATUS_AT_DESK:
                return (self.ACT_ANNOUNCE_FALSE_ALARM, self.ACT_ANNOUNCE_REAL_ALARM, self.ACT_MOVE_TO_EXIT, self.ACT_STAY_AT_DESK)
            elif manager_status == self.STATUS_MOVING:
                return (self.ACT_ANNOUNCE_FALSE_ALARM, self.ACT_ANNOUNCE_REAL_ALARM, self.ACT_MOVE_TO_EXIT, self.ACT_STAY_AT_DESK)
            else:
                return (self.ACT_NOOP,)

        return (self.ACT_NOOP,)

    def transition(self, s: S, a: Tuple[str, str, str]) -> Mapping[Tuple[S, Tuple[str, str, str]], float]:
        if self.is_terminal(s):
            # Stay in terminal state
            obs = (self.OBS_AT_EXIT, self.OBS_AT_EXIT, self.OBS_AT_EXIT)
            return {((s, obs)): 1.0}

        phase, wheelchair_status, desk_status, manager_status = s
        a_wheelchair, a_desk, a_manager = a

        # Update statuses based on actions
        # Wheelchair: Moving takes time? Let's assume one step moves them to 'moving', next step to 'exit'.
        # Or simpler: 'move_to_exit' transitions AT_DESK -> MOVING, MOVING -> AT_EXIT.
        
        new_wheelchair_status = wheelchair_status
        if a_wheelchair == self.ACT_MOVE_TO_EXIT:
            if wheelchair_status == self.STATUS_AT_DESK:
                new_wheelchair_status = self.STATUS_MOVING
            elif wheelchair_status == self.STATUS_MOVING:
                new_wheelchair_status = self.STATUS_AT_EXIT
            # If already at exit, stays at exit

        new_desk_status = desk_status
        if a_desk == self.ACT_MOVE_TO_EXIT:
            if desk_status == self.STATUS_AT_DESK:
                new_desk_status = self.STATUS_MOVING
            elif desk_status == self.STATUS_MOVING:
                new_desk_status = self.STATUS_AT_EXIT
            # If already at exit, stays at exit

        new_manager_status = manager_status
        if a_manager == self.ACT_MOVE_TO_EXIT:
            if manager_status == self.STATUS_AT_DESK:
                new_manager_status = self.STATUS_MOVING
            elif manager_status == self.STATUS_MOVING:
                new_manager_status = self.STATUS_AT_EXIT
            # If already at exit, stays at exit

        # Determine if the situation is resolved.
        # The situation implies a conflict between evacuating and staying.
        # Resolution happens when everyone has made a final decision and reached their destination?
        # Or does it resolve when the manager's announcement is heard and accepted?
        # Let's define resolution as: All players are at their final positions (Exit or Desk) 
        # AND no one is currently moving.
        
        # Actually, "Resolved" should probably mean the interaction is over.
        # If everyone is at the exit, the evacuation is complete.
        # If everyone is at the desk, the false alarm is confirmed/accepted.
        # Mixed states are unstable?
        
        # Let's say the game ends when all players are either at the exit or at the desk, 
        # and no one is in transit.
        
        all_settled = (new_wheelchair_status in [self.STATUS_AT_DESK, self.STATUS_AT_EXIT] and
                       new_desk_status in [self.STATUS_AT_DESK, self.STATUS_AT_EXIT] and
                       new_manager_status in [self.STATUS_AT_DESK, self.STATUS_AT_EXIT])
        
        # But wait, if someone is at desk and someone at exit, is it resolved?
        # The prompt says "one is in a wheelchair... another stays... manager tells everyone false alarm".
        # This suggests a specific dynamic. 
        # Let's assume the game ends when everyone has stopped moving.
        
        if all_settled:
            new_phase = self.PHASE_RESOLVED
        else:
            new_phase = self.PHASE_ALARM

        new_state = self._make_state(new_phase, new_wheelchair_status, new_desk_status, new_manager_status)

        # Generate Observations
        # Observations depend on what happened this step.
        # If manager announced, others hear it.
        
        obs_wheelchair = self.OBS_NONE
        obs_desk = self.OBS_NONE
        obs_manager = self.OBS_NONE

        # Base observations: see own status
        if new_wheelchair_status == self.STATUS_AT_DESK:
            obs_wheelchair = self.OBS_AT_DESK
        elif new_wheelchair_status == self.STATUS_MOVING:
            obs_wheelchair = self.OBS_MOVING
        else:
            obs_wheelchair = self.OBS_AT_EXIT

        if new_desk_status == self.STATUS_AT_DESK:
            obs_desk = self.OBS_AT_DESK
        elif new_desk_status == self.STATUS_MOVING:
            obs_desk = self.OBS_MOVING
        else:
            obs_desk = self.OBS_AT_EXIT

        if new_manager_status == self.STATUS_AT_DESK:
            obs_manager = self.OBS_AT_DESK
        elif new_manager_status == self.STATUS_MOVING:
            obs_manager = self.OBS_MOVING
        else:
            obs_manager = self.OBS_AT_EXIT

        # Manager's announcement affects others
        if a_manager == self.ACT_ANNOUNCE_FALSE_ALARM:
            # Others hear the false alarm announcement
            # They might update their belief, but here we just record the observation
            obs_wheelchair = self.OBS_HEARD_FALSE_ALARM
            obs_desk = self.OBS_HEARD_FALSE_ALARM
            # Manager hears themselves? Or just sees their action?
            # Let's say manager observes their own action as 'announced_false'
            obs_manager = self.OBS_HEARD_FALSE_ALARM 

        elif a_manager == self.ACT_ANNOUNCE_REAL_ALARM:
            obs_wheelchair = self.OBS_HEARD_REAL_ALARM
            obs_desk = self.OBS_HEARD_REAL_ALARM
            obs_manager = self.OBS_HEARD_REAL_ALARM

        # If phase is resolved, override with final state observation?
        # The rules say: "A player who observes nothing new still gets an observation: use none..."
        # But if the game ends, they know the outcome.
        # Let's stick to the immediate perception.
        
        obs_profile = (obs_wheelchair, obs_desk, obs_manager)

        return {((new_state, obs_profile)): 1.0}

    def rewards(self, s: S, a: Tuple[str, str, str], s_next: S) -> Tuple[float, float, float]:
        return (0.0, 0.0, 0.0)
