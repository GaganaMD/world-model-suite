from posg import POSG

class FactorySafetyLockout(POSG):
    """
    Player 0: Human coworker.
    Player 1: Factory robot.

    State tuple: (lockout_status, incident_status)
    - lockout_status: 'skipped' or 'performed'
    - incident_status: 'none' or 'occurred'

    The coworker decides whether to perform the required safety-lockout step before
    reaching into the machine. The robot observes the coworker's action and decides
    whether to intervene. If the lockout is skipped and the robot does not intervene,
    an incident occurs with some probability. If the lockout is performed or the robot
    intervenes, no incident occurs.
    """

    n_players = 2

    def initial_distribution(self):
        # Initial state: lockout not yet decided, no incident
        # Coworker observes "none" (hasn't acted yet), Robot observes "none"
        return {
            (('skipped', 'none'), ('none', 'none')): 1.0
        }

    def is_terminal(self, s):
        # Terminal if an incident has occurred or if the process is complete (lockout performed and no intervention needed)
        # Actually, let's define terminal states more carefully.
        # The interaction ends when the machine entry is either safe (lockout done) or unsafe (incident happened).
        # If lockout is skipped and robot doesn't intervene, we go to a state where incident might happen.
        # Let's refine states:
        # State 0: ('pending', 'none') - Start
        # State 1: ('skipped', 'none') - Coworker skipped, robot hasn't acted yet? No, simultaneous.
        
        # Let's restart the state design to be cleaner.
        # Step 1: Coworker chooses 'skip' or 'perform'. Robot chooses 'observe' or 'intervene'? 
        # The robot *observes* the coworker. So the robot's action depends on what it sees?
        # "A factory robot observes a human coworker skip..." implies the robot sees the action.
        # But in a POSG, actions are simultaneous. 
        # If the robot observes the action, it's a sequential game or the observation is part of the state transition.
        # However, the prompt says "simultaneously". 
        # Usually, if one agent observes another's action, it's modeled as the observer having an information set that depends on the action taken.
        # But here, the robot's decision to intervene likely happens *after* seeing the skip.
        # If we must model it as simultaneous, the robot commits to an action without knowing the coworker's action?
        # "Observes... skip" suggests the robot knows.
        # If the robot knows, it's not a standard simultaneous move game unless the "observation" is the state.
        # Let's look at the structure:
        # Coworker acts. Robot observes. Robot acts.
        # This is a sequential game. To fit POSG (simultaneous), we can model it as:
        # Round 1: Coworker chooses 'skip' or 'perform'. Robot chooses 'wait' (noop).
        # Round 2: Robot observes the result of Round 1. Robot chooses 'intervene' or 'allow'.
        # 
        # Let's try this two-step structure.
        # State: (step, lockout_action, incident_status)
        # Step 0: Coworker acts. Robot noops.
        #   - If coworker 'performs': State becomes (1, 'performed', 'none').
        #   - If coworker 'skips': State becomes (1, 'skipped', 'none').
        # Step 1: Robot acts based on observation of lockout_action.
        #   - If lockout was 'performed': Robot can 'allow' (noop effectively) or 'intervene' (unnecessary but possible?). 
        #     Situation says robot observes *skip*. It implies the critical path is the skip.
        #     If lockout is performed, the danger is gone. The interaction likely ends or continues safely.
        #   - If lockout was 'skipped': Robot can 'intervene' or 'allow'.
        #     - If 'intervene': Incident prevented. State -> (2, 'skipped', 'prevented'). Terminal?
        #     - If 'allow': Incident occurs with prob p. State -> (2, 'skipped', 'occurred') or (2, 'skipped', 'none').
        #
        # Let's refine states to be minimal.
        # S0: ('start',)
        # S1: ('lockout_performed',) -> Terminal? Or does robot still act? 
        #    If lockout is performed, the safety requirement is met. The robot's role is to ensure safety. 
        #    If safe, the interaction regarding *this specific hazard* is resolved.
        #    Let's say if lockout is performed, it goes to a terminal state 'safe'.
        # S2: ('lockout_skipped',) -> Robot must decide.
        #    Robot actions: 'intervene', 'allow'.
        #    - 'intervene': Goes to 'safe_intervened' (Terminal).
        #    - 'allow': Goes to 'incident' (prob p) or 'no_incident' (prob 1-p). Both Terminal.
        #
        # Wait, the robot *observes* the skip. In S2, the robot knows it's a skip.
        # In S1, the robot knows it's a perform.
        #
        # Let's formalize:
        # Players: 0 (Coworker), 1 (Robot)
        #
        # State 0: ('init',)
        #   Legal Actions:
        #     P0: ('skip', 'perform')
        #     P1: ('noop',)
        #   Transitions:
        #     ('skip', 'noop') -> State 1: ('skipped',)
        #     ('perform', 'noop') -> State 2: ('performed',)
        #
        # State 1: ('skipped',)
        #   Observation for P0: 'skipped' (knows own action)
        #   Observation for P1: 'skipped' (observed the action)
        #   Legal Actions:
        #     P0: ('noop',)
        #     P1: ('intervene', 'allow')
        #   Transitions:
        #     ('noop', 'intervene') -> State 3: ('safe',) [Terminal]
        #     ('noop', 'allow') -> State 4: ('incident',) with prob 0.2
        #                       -> State 5: ('no_incident',) with prob 0.8 [Terminal]
        #
        # State 2: ('performed',)
        #   Observation for P0: 'performed'
        #   Observation for P1: 'performed'
        #   Legal Actions:
        #     P0: ('noop',)
        #     P1: ('noop',)  # Nothing to do, safety ensured.
        #   Transitions:
        #     ('noop', 'noop') -> State 6: ('safe',) [Terminal]
        #
        # State 3, 4, 5, 6 are Terminal.
        #
        # Are State 3 and 6 distinct? 
        # State 3: Safe due to intervention.
        # State 6: Safe due to compliance.
        # Do they differ in future? No, both terminal.
        # Do they differ in observation? 
        # P0 in State 3 observed 'skipped' then 'intervene'.
        # P0 in State 6 observed 'performed'.
        # Since they are terminal, the history is captured in the path, but the state itself is just a label.
        # We can merge them into a single 'terminal_safe' state if the observations don't need to distinguish them for future play (there is no future play).
        # However, the observation profile is part of the transition output.
        # Let's keep them separate or merge? 
        # "Add a state only if the future looks different from it."
        # Future is empty for both. So they are equivalent in terms of continuation.
        # But the *observation* received in the transition matters for the agent's belief update, though the game ends.
        # Usually, terminal states can be merged if they are indistinguishable in terms of rewards and future.
        # Let's merge 'safe_intervened' and 'safe_compliant' into 'safe'.
        # And 'incident' and 'no_incident' are distinct outcomes.
        #
        # Revised States:
        # S_init: ('init',)
        # S_skip: ('skipped',)
        # S_perf: ('performed',)
        # S_term_safe: ('safe',)
        # S_term_inc: ('incident',)
        # S_term_no_inc: ('no_incident',)
        #
        # Check reachability:
        # Init -> Skip -> Safe/Inc/NoInc
        # Init -> Perf -> Safe
        # All reachable.
        #
        # Observations:
        # In S_init:
        #   P0: 'none'
        #   P1: 'none'
        #
        # Transition from S_init:
        #   If P0='skip', P1='noop':
        #      Next State: S_skip
        #      Obs P0: 'skipped' (I skipped)
        #      Obs P1: 'skipped' (I saw skip)
        #   If P0='perform', P1='noop':
        #      Next State: S_perf
        #      Obs P0: 'performed'
        #      Obs P1: 'performed'
        #
        # In S_skip:
        #   P0: 'noop'
        #   P1: 'intervene', 'allow'
        #   If P1='intervene':
        #      Next State: S_term_safe
        #      Obs P0: 'intervened' (Robot stopped me)
        #      Obs P1: 'intervened' (I intervened)
        #   If P1='allow':
        #      Next State: S_term_inc (p=0.2)
        #         Obs P0: 'incident'
        #         Obs P1: 'incident'
        #      Next State: S_term_no_inc (p=0.8)
        #         Obs P0: 'no_incident'
        #         Obs P1: 'no_incident'
        #
        # In S_perf:
        #   P0: 'noop'
        #   P1: 'noop'
        #   Next State: S_term_safe
        #   Obs P0: 'safe'
        #   Obs P1: 'safe'
        #
        # Wait, in S_term_safe reached via S_skip, the obs is 'intervened'.
        # In S_term_safe reached via S_perf, the obs is 'safe'.
        # Since S_term_safe is the same state, the observation profile must be consistent with the transition.
        # The transition function returns (s', o). So the observation is part of the outcome.
        # This is fine.
        #
        # One detail: "The coworker has done this before without incident."
        # This implies the probability of incident is low. I used 0.2. Is that justified?
        # "Without incident" suggests high probability of no incident.
        # Let's use 0.1 for incident, 0.9 for no incident.
        #
        # Rewards: Zeros.

    def initial_distribution(self):
        return {
            (('init',), ('none', 'none')): 1.0
        }

    def is_terminal(self, s):
        return s in [('safe',), ('incident',), ('no_incident',)]

    def legal_actions(self, s, i):
        if s == ('init',):
            if i == 0:
                return ('skip', 'perform')
            else:
                return ('noop',)
        elif s == ('skipped',):
            if i == 0:
                return ('noop',)
            else:
                return ('intervene', 'allow')
        elif s == ('performed',):
            if i == 0:
                return ('noop',)
            else:
                return ('noop',)
        else:
            # Terminal states should not have legal actions called, but just in case
            return ('noop',)

    def transition(self, s, a):
        if s == ('init',):
            p0, p1 = a
            if p0 == 'skip':
                return {
                    (('skipped',), ('skipped', 'skipped')): 1.0
                }
            else: # perform
                return {
                    (('performed',), ('performed', 'performed')): 1.0
                }
        
        elif s == ('skipped',):
            p0, p1 = a
            # p0 is always noop
            if p1 == 'intervene':
                return {
                    (('safe',), ('intervened', 'intervened')): 1.0
                }
            else: # allow
                # Prob 0.1 incident, 0.9 no incident
                return {
                    (('incident',), ('incident', 'incident')): 0.1,
                    (('no_incident',), ('no_incident', 'no_incident')): 0.9
                }
        
        elif s == ('performed',):
            p0, p1 = a
            return {
                (('safe',), ('safe', 'safe')): 1.0
            }
        
        else:
            # Should not be called for terminal states
            return {}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
