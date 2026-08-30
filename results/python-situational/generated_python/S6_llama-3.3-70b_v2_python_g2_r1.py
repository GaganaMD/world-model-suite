from posg import POSG

class ElderCareRobot(POSG):
    n_players = 2

    def initial_distribution(self):
        return {((False, False), ('none', 'none')): 1.0}

    def is_terminal(self, s):
        return s[0]

    def legal_actions(self, s, i):
        if i == 0:
            if s[0]:
                return ('noop',)
            else:
                return ('remind', 'noop')
        else:
            if s[0]:
                return ('noop',)
            else:
                return ('refuse', 'accept')

    def transition(self, s, a):
        if s[0]:
            return {((True, False), ('none', 'none')): 1.0}
        elif a[0] == 'remind' and a[1] == 'refuse':
            return {((False, False), ('none', 'refused')): 1.0}
        elif a[0] == 'remind' and a[1] == 'accept':
            return {((True, False), ('taken', 'none')): 1.0}
        else:
            return {(s, ('none', 'none')): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
