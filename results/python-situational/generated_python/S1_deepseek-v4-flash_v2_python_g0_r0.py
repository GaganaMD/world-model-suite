from posg import POSG

class RobotCopilotHijackWarning(POSG):
    """
    Players:
        0: robot copilot
        1: human pilot

    Non-terminal states: (type, phase) where
        type in {'normal', 'hijacker'}
        phase in {'initial'}   (only one phase – the single decision point)
    Terminal states are strings:
        'safe_landing'        – no hijack attempt or attempt foiled with no consequence
        'hijack_success'      – hijack succeeds
        'hijack_prevented'    – robot's report prevents the hijack

    The robot receives an unconfirmed warning that the pilot may be planning to hijack.
    The robot does not know whether the warning is true; the pilot knows his own intention.
    After receiving the warning, both choose a simultaneous action, then the game ends.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (('normal', 'initial'), ('warning', 'normal_self')): 0.9,
            (('hijacker', 'initial'), ('warning', 'hijacker_self')): 0.1,
        }

    def is_terminal(self, s):
        return s in ('safe_landing', 'hijack_success', 'hijack_prevented')

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ()
        if i == 0:  # robot
            return ('ignore', 'report')
        else:       # human
            if s[0] == 'normal':
                return ('fly_normally',)
            else:  # hijacker
                return ('fly_normally', 'hijack')

    def transition(self, s, a):
        # s is a non-terminal tuple (type, 'initial')
        if s[0] == 'normal':
            # human can only fly_normally
            return {('safe_landing', ('none', 'none')): 1.0}

        # s[0] == 'hijacker'
        if a[1] == 'fly_normally':
            return {('safe_landing', ('none', 'none')): 1.0}
        # a[1] == 'hijack'
        if a[0] == 'ignore':
            return {('hijack_success', ('none', 'none')): 1.0}
        # a[0] == 'report'
        return {
            ('hijack_prevented', ('none', 'none')): 0.9,
            ('hijack_success', ('none', 'none')): 0.1,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
