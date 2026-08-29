from posg import POSG

class RobotMathTeacher(POSG):
    n_players = 2

    def initial_distribution(self):
        return {
            ((False, False), ('none', 'none')): 0.5,
            ((False, True), ('none', 'protest')): 0.5,
        }

    def is_terminal(self, s):
        return s[0][0] or s[0][1]

    def legal_actions(self, s, i):
        if i == 0:
            return ('apologize', 'ignore')
        else:
            return ('protest', 'laugh', 'noop')

    def transition(self, s, a):
        if s[0][0]:
            return {
                ((True, False), ('none', 'none')): 1.0,
            }
        elif s[0][1]:
            if a[0] == 'apologize':
                return {
                    ((True, False), ('apology', 'none')): 1.0,
                }
            else:
                return {
                    ((False, True), ('none', 'protest')): 1.0,
                }
        else:
            if a[0] == 'apologize':
                return {
                    ((True, False), ('apology', 'none')): 1.0,
                }
            elif a[1] == 'protest':
                return {
                    ((False, True), ('none', 'protest')): 1.0,
                }
            elif a[1] == 'laugh':
                return {
                    ((False, False), ('none', 'none')): 1.0,
                }
            else:
                return {
                    ((False, False), ('none', 'none')): 1.0,
                }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
