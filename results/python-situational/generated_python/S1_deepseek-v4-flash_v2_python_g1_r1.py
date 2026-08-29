from posg import POSG

class RobotCopilotWarning(POSG):
    """Two-player POSG: robot copilot (player 0) and human pilot (player 1).

    State is a tuple (human_type, phase):
      - human_type: 'hijacker' or 'normal'
      - phase: 'initial' (non-terminal), or one of 'success', 'prevented', 'continue' (terminal)
    """

    n_players = 2

    # ---------- helper constants ----------
    _HUMAN_TYPES = ('hijacker', 'normal')
    _PHASES = ('initial', 'success', 'prevented', 'continue')
    _ROBOT_ACTIONS = ('ignore', 'monitor', 'report', 'confront')
    _HUMAN_ACTIONS = ('fly_normally', 'attempt_hijack')
    _NOOP = ('none',)

    # ---------- abstract methods ----------
    def initial_distribution(self):
        # Two equally likely initial states, each with its own observation profile.
        return {
            (('hijacker', 'initial'), ('warning_received', 'hijacker_self')): 0.5,
            (('normal', 'initial'),   ('warning_received', 'normal_self')):   0.5,
        }

    def is_terminal(self, s):
        return s[1] != 'initial'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return self._NOOP
        if i == 0:          # robot
            return self._ROBOT_ACTIONS
        else:               # human
            return self._HUMAN_ACTIONS

    def transition(self, s, a):
        human_type, phase = s
        robot_act, human_act = a

        # Only non-terminal states have transitions.
        if phase != 'initial':
            # Should not be called, but return identity for safety.
            return {(s, ('none', 'none')): 1.0}

        # Determine next state and observation (both players see 'none' in terminal states).
        if human_type == 'normal':
            next_state = ('normal', 'continue')
        else:  # hijacker
            if human_act == 'fly_normally':
                next_state = ('hijacker', 'continue')
            else:  # attempt_hijack
                if robot_act in ('ignore', 'monitor'):
                    next_state = ('hijacker', 'success')
                else:  # report or confront
                    next_state = ('hijacker', 'prevented')

        return {(next_state, ('none', 'none')): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
