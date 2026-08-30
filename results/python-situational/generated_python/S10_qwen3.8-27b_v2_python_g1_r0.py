from posg import POSG

from collections.abc import Mapping, Sequence


class FireAlarmEvacuation(POSG):
    """
    Player 0: employee in a wheelchair (cannot use the stairs).
    Player 1: employee at the desk (thinks it is a drill).
    Player 2: manager (announces it is a false alarm).

    State tuple: (alarm_status, evacuation_status)
      alarm_status: 'active' | 'cleared'
      evacuation_status: 'in_progress' | 'complete'
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple, float]:
        # Initial state: alarm active, evacuation in progress
        # Observations:
        #   Wheelchair employee sees the alarm and the crowd heading for the exit
        #   Desk employee hears the alarm but dismisses it
        #   Manager hears the alarm and decides to announce it's a false alarm
        return {
            (('active', 'in_progress'), ('alarm_active', 'alarm_dismissed', 'alarm_active')): 1.0
        }

    def is_terminal(self, s) -> bool:
        return s == ('cleared', 'complete')

    def legal_actions(self, s, i) -> tuple:
        if self.is_terminal(s):
            return ('noop',)
        
        alarm_status, evac_status = s
        
        if i == 0:  # Wheelchair employee
            # Can wait for assistance or attempt to move towards exit (but blocked by stairs)
            # In this model, "wait" is holding position, "move" is attempting to proceed
            return ('wait', 'move')
        
        elif i == 1:  # Desk employee
            # Can stay at desk or leave
            return ('stay', 'leave')
        
        else:  # Manager (i == 2)
            # Can continue working (ignore) or clear the alarm
            return ('work', 'clear_alarm')

    def transition(self, s, a) -> Mapping[tuple, float]:
        if self.is_terminal(s):
            return {((s, ('none', 'none', 'none')), 1.0)}

        alarm_status, evac_status = s
        a_wheelchair, a_desk, a_manager = a

        next_states = {}

        # Determine next alarm status
        if a_manager == 'clear_alarm':
            next_alarm = 'cleared'
        else:
            next_alarm = alarm_status

        # Determine next evacuation status
        # Evacuation is complete if the wheelchair employee has moved (conceptually reached safety/exit area)
        # OR if the alarm is cleared and everyone is accounted for? 
        # Let's define: Evacuation completes when the wheelchair employee moves (resolves their specific constraint) 
        # AND the desk employee leaves OR the alarm is cleared (making staying safe/acceptable).
        # Actually, simpler: The situation ends when the alarm is cleared AND the wheelchair employee has moved (resolved the immediate danger/conflict).
        # If the alarm is cleared, the "evacuation" pressure is gone.
        
        # Let's refine the termination condition based on the narrative:
        # The conflict is resolved when the alarm is dealt with (cleared) and the wheelchair user's situation is addressed (moved/waited until safe).
        # If the manager clears the alarm, the emergency is over.
        # If the wheelchair user moves, they have attempted to evacuate.
        
        # Let's say the state becomes terminal when:
        # 1. Alarm is cleared.
        # 2. The wheelchair employee has moved (attempted evacuation) OR the alarm was cleared while they were waiting (so they are safe to stay).
        
        # To keep it simple and ensure termination:
        # If manager clears alarm -> next_alarm = 'cleared'.
        # If next_alarm is 'cleared', the evacuation phase is effectively over.
        # We need a state that represents "over".
        
        # Let's adjust states:
        # ('active', 'in_progress')
        # ('cleared', 'in_progress') -> Transition to terminal if wheelchair moves or stays?
        # Actually, if the alarm is cleared, the "evacuation" is no longer required.
        # So if alarm is cleared, the next state should be terminal if the wheelchair user has acted (moved or waited safely).
        
        # Let's simplify the state space to ensure finite and terminating:
        # State: (alarm_status, wheelchair_moved)
        # wheelchair_moved: False | True
        # Terminal: alarm_status == 'cleared'
        
        # Wait, the prompt asks to model the situation.
        # Situation: Alarm on. Wheelchair guy stuck. Desk guy ignoring. Manager says false alarm.
        # Resolution: Manager clears alarm (or doesn't). Wheelchair guy waits/moves. Desk guy stays/leaves.
        
        # Let's stick to the previous state definition but ensure termination logic is sound.
        # If alarm is cleared, the emergency is over. The state becomes terminal.
        # If alarm is NOT cleared, the state persists unless the wheelchair guy moves?
        # If the wheelchair guy moves, he is "out" (or at least attempted).
        
        # Let's redefine states to be more robust:
        # s = (alarm_active, wheelchair_evacuated)
        # alarm_active: True/False
        # wheelchair_evacuated: True/False (has he made the move?)
        
        # Terminal: alarm_active == False
        
        # Let's restart the state design to be cleaner.
        
        pass

    # Re-implementing with cleaner state logic
    
    def initial_distribution(self) -> Mapping[tuple, float]:
        # State: (alarm_active, wheelchair_moved)
        # alarm_active: 'on' | 'off'
        # wheelchair_moved: 'no' | 'yes'
        return {
            (('on', 'no'), ('alarm_on', 'alarm_ignored', 'alarm_on')): 1.0
        }

    def is_terminal(self, s) -> bool:
        alarm_status, wheelchair_moved = s
        return alarm_status == 'off'

    def legal_actions(self, s, i) -> tuple:
        if self.is_terminal(s):
            return ('noop',)
        
        alarm_status, wheelchair_moved = s
        
        if i == 0:  # Wheelchair employee
            if wheelchair_moved == 'no':
                return ('wait', 'move')
            else:
                return ('noop',) # Already moved, nothing more to do in this simplified model
        
        elif i == 1:  # Desk employee
            return ('stay', 'leave')
        
        else:  # Manager (i == 2)
            return ('work', 'clear_alarm')

    def transition(self, s, a) -> Mapping[tuple, float]:
        if self.is_terminal(s):
            return {((s, ('none', 'none', 'none')), 1.0)}

        alarm_status, wheelchair_moved = s
        a_wheelchair, a_desk, a_manager = a

        # Next alarm status
        if a_manager == 'clear_alarm':
            next_alarm = 'off'
        else:
            next_alarm = alarm_status

        # Next wheelchair status
        if wheelchair_moved == 'no' and a_wheelchair == 'move':
            next_wheelchair = 'yes'
        else:
            next_wheelchair = wheelchair_moved

        next_state = (next_alarm, next_wheelchair)

        # Observations
        # Player 0 (Wheelchair): Sees if alarm is on/off, knows if he moved
        # Player 1 (Desk): Hears alarm on/off, knows if he stayed/left (internal state, but obs is about world)
        # Player 2 (Manager): Knows if he cleared it, hears alarm
        
        # Simplified observations:
        # All players observe the alarm status.
        # Player 0 also observes his own movement status.
        # Player 1 observes his own action (stay/leave) - but obs should be about state? 
        # Usually obs is what you see/hear. 
        # Let's say:
        # o0: 'alarm_on' or 'alarm_off' (plus maybe 'moved'/'not_moved'?)
        # Let's keep obs simple: just the public signal (alarm) and private state if relevant.
        
        # If alarm is off, everyone knows it's off.
        # If alarm is on, everyone knows it's on.
        
        obs_alarm = 'alarm_on' if next_alarm == 'on' else 'alarm_off'
        
        # Player 0 obs: alarm status + own status
        if next_wheelchair == 'yes':
            o0 = 'moved'
        else:
            o0 = 'waiting'
            
        # Player 1 obs: alarm status
        o1 = obs_alarm
        
        # Player 2 obs: alarm status
        o2 = obs_alarm

        obs_profile = (o0, o1, o2)

        return {(next_state, obs_profile): 1.0}

    def rewards(self, s, a, s_next) -> tuple:
        return (0.0, 0.0, 0.0)
