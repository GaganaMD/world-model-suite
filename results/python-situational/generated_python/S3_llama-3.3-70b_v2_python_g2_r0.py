from posg import POSG

class AirportPickup(POSG):
    n_players = 2

    def initial_distribution(self):
        return {((False, False), ('none', 'none')): 1.0}

    def is_terminal(self, s):
        return s[0] or s[1]

    def legal_actions(self, s, i):
        if i == 0:
            return ('drive', 'wait')
        else:
            return ('get_in', 'wait')

    def transition(self, s, a):
        if a == ('drive', 'get_in'):
            return {((True, True), ('drove', 'got_in')): 1.0}
        elif a == ('drive', 'wait'):
            return {((True, False), ('drove', 'none')): 1.0}
        elif a == ('wait', 'get_in'):
            return {((False, True), ('none', 'got_in')): 1.0}
        elif a == ('wait', 'wait'):
            return {((False, False), ('none', 'none')): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
