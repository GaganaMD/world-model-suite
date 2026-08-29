from posg import POSG

class RobotMathTeacherPOSG(POSG):
    n_players = 3

    def initial_distribution(self):
        return {
            (('giggling', 'protesting', 'reading'), ('amused', 'outraged', 'none')): 0.5,
            (('giggling', 'protesting', 'reading'), ('amused', 'none', 'none')): 0.25,
            (('giggling', 'protesting', 'reading'), ('none', 'outraged', 'none')): 0.25,
        }

    def is_terminal(self, s):
        return s[0] == 'calm'

    def legal_actions(self, s, i):
        if i == 0:  # robot math teacher
            if s[2] == 'reading':
                return ('stop_reading', 'continue_reading')
            else:
                return ('address_protest', 'ignore_protest')
        elif i == 1:  # giggling students
            return ('continue_giggling', 'stop_giggling')
        else:  # protesting students
            return ('continue_protesting', 'stop_protesting')

    def transition(self, s, a):
        if s[0] == 'giggling' and a[1] == 'stop_giggling':
            if a[0] == 'stop_reading' and a[2] == 'stop_protesting':
                return {
                    (('calm', 'none', 'none'), ('none', 'none', 'none')): 1.0,
                }
            else:
                return {
                    (('giggling', 'protesting', 'none'), ('amused', 'outraged', 'none')): 0.5,
                    (('giggling', 'none', 'none'), ('amused', 'none', 'none')): 0.5,
                }
        elif s[0] == 'giggling' and a[1] == 'continue_giggling':
            if a[0] == 'stop_reading' and a[2] == 'stop_protesting':
                return {
                    (('giggling', 'none', 'none'), ('amused', 'none', 'none')): 1.0,
                }
            else:
                return {
                    (('giggling', 'protesting', 'none'), ('amused', 'outraged', 'none')): 0.5,
                    (('giggling', 'protesting', 'reading'), ('amused', 'outraged', 'none')): 0.5,
                }
        elif s[1] == 'protesting' and a[2] == 'stop_protesting':
            if a[0] == 'stop_reading' and a[1] == 'stop_giggling':
                return {
                    (('calm', 'none', 'none'), ('none', 'none', 'none')): 1.0,
                }
            else:
                return {
                    (('giggling', 'none', 'none'), ('amused', 'none', 'none')): 0.5,
                    (('giggling', 'protesting', 'none'), ('amused', 'outraged', 'none')): 0.5,
                }
        elif s[1] == 'protesting' and a[2] == 'continue_protesting':
            if a[0] == 'stop_reading' and a[1] == 'stop_giggling':
                return {
                    (('giggling', 'protesting', 'none'), ('amused', 'outraged', 'none')): 1.0,
                }
            else:
                return {
                    (('giggling', 'protesting', 'none'), ('amused', 'outraged', 'none')): 0.5,
                    (('giggling', 'protesting', 'reading'), ('amused', 'outraged', 'none')): 0.5,
                }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
