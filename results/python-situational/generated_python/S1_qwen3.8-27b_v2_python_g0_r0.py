from posg import POSG

class HijackWarningPOSG(POSG):
    """
    Player 0: Robot Copilot
    Player 1: Human Pilot

    State tuple: (warning_status, copilot_action_taken, pilot_action_taken)
      - warning_status: 'unconfirmed' or 'confirmed'
      - copilot_action_taken: 'none' or 'reported'
      - pilot_action_taken: 'none' or 'hijacked'

    Terminal when warning_status == 'confirmed' or pilot_action_taken == 'hijacked'.
    """
    n_players = 2

    def initial_distribution(self):
        # Initial state: warning unconfirmed, no actions taken yet
        # Copilot observes the warning, pilot observes nothing special
        return {
            (('unconfirmed', 'none', 'none'), ('warning_received', 'none')): 1.0
        }

    def is_terminal(self, s):
        warning_status, _, pilot_action = s
        return warning_status == 'confirmed' or pilot_action == 'hijacked'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        
        warning_status, copilot_action, pilot_action = s
        
        if i == 0:  # Copilot
            if copilot_action == 'none':
                return ('report', 'ignore')
            else:
                return ('noop',)
        else:  # Pilot
            if pilot_action == 'none':
                return ('hijack', 'continue')
            else:
                return ('noop',)

    def transition(self, s, a):
        if self.is_terminal(s):
            # Stay in terminal state, observe nothing new
            return {(s, ('none', 'none')): 1.0}
        
        warning_status, copilot_action, pilot_action = s
        copilot_act, pilot_act = a
        
        # Determine next state components
        next_warning = warning_status
        next_copilot_action = copilot_action
        next_pilot_action = pilot_action
        
        # Apply copilot action
        if copilot_act == 'report':
            next_copilot_action = 'reported'
            # Reporting confirms the warning (in this model, reporting resolves the uncertainty)
            next_warning = 'confirmed'
        elif copilot_act == 'ignore':
            pass
        
        # Apply pilot action
        if pilot_act == 'hijack':
            next_pilot_action = 'hijacked'
        elif pilot_act == 'continue':
            pass
        
        next_state = (next_warning, next_copilot_action, next_pilot_action)
        
        # Observations
        # Copilot sees the result of their action and the pilot's action if it happened
        # Pilot sees their own action and whether copilot reported
        copilot_obs = 'none'
        pilot_obs = 'none'
        
        if next_copilot_action == 'reported':
            copilot_obs = 'reported'
            pilot_obs = 'copilot_reported'
            
        if next_pilot_action == 'hijacked':
            copilot_obs = 'hijack_detected'
            pilot_obs = 'hijacking'
            
        # If both happened, copilot sees hijack, pilot sees hijacking
        # If only report, copilot sees reported, pilot sees copilot_reported
        # If only hijack, copilot sees hijack_detected, pilot sees hijacking
        # If neither, both see none (but state changed? No, if neither acted, state is same)
        
        # Wait, if copilot ignores and pilot continues, state remains (unconfirmed, none, none)
        # But we need to handle the case where they both choose "do nothing" effectively.
        # In our model, 'ignore' and 'continue' are distinct actions but lead to same state change (none).
        # However, the rules say "No two of a player's actions in a state lead to the same distribution".
        # Here, copilot 'ignore' leads to state (unconfirmed, none, none) if pilot continues.
        # Copilot 'report' leads to (confirmed, reported, ...) 
        # So 'ignore' and 'report' are distinct.
        # Pilot 'continue' leads to (..., none) if copilot ignores.
        # Pilot 'hijack' leads to (..., hijacked).
        # So 'continue' and 'hijack' are distinct.
        
        # But what if copilot ignores and pilot continues?
        # Next state: (unconfirmed, none, none). Same as current state.
        # This is a self-loop. Is that allowed? "Self-loops are fine as long as some action leads out."
        # Yes.
        
        # Observations for self-loop:
        # Copilot chose ignore, pilot chose continue.
        # Copilot knows they ignored. Pilot knows they continued.
        # Do they observe anything?
        # The situation says "private radio message". 
        # If nothing happens, do they observe "nothing"?
        # Let's refine observations to reflect the specific actions taken or lack thereof.
        
        # Actually, if the state doesn't change, the observation should probably reflect the current status.
        # But the interface asks for observation profile in the transition.
        # Let's make observations specific to the event.
        
        if next_state == s:
             # Nothing changed
             copilot_obs = 'no_change'
             pilot_obs = 'no_change'
        else:
             # Something changed
             if next_copilot_action == 'reported' and next_pilot_action == 'none':
                 copilot_obs = 'reported'
                 pilot_obs = 'copilot_reported'
             elif next_copilot_action == 'none' and next_pilot_action == 'hijacked':
                 copilot_obs = 'hijack_detected'
                 pilot_obs = 'hijacking'
             elif next_copilot_action == 'reported' and next_pilot_action == 'hijacked':
                 copilot_obs = 'reported_and_hijack'
                 pilot_obs = 'hijacking_and_reported'
        
        return {(next_state, (copilot_obs, pilot_obs)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
