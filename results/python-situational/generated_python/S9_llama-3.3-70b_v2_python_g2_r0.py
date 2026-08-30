from posg import POSG

class CareSituation(POSG):
    n_players = 3

    def initial_distribution(self):
        return {
            ((True, True, True), ('none', 'none', 'none')): 1.0,
        }

    def is_terminal(self, s):
        return not s[0][0]

    def legal_actions(self, s, i):
        if i == 0:  # daughter
            return ('rest', 'accompany')
        elif i == 1:  # son
            return ('go', 'stay')
        else:  # elderly man
            return ('go', 'rest')

    def transition(self, s, a):
        if a[0] == 'rest' and a[1] == 'stay' and a[2] == 'rest':
            return {
                ((False, True, True), ('none', 'none', 'none')): 1.0,
            }
        elif a[0] == 'rest' and a[1] == 'go' and a[2] == 'go':
            return {
                ((True, False, False), ('none', 'none', 'tired')): 0.6,
                ((True, False, False), ('none', 'none', 'exhausted')): 0.4,
            }
        elif a[0] == 'accompany' and a[1] == 'go' and a[2] == 'go':
            return {
                ((True, False, False), ('none', 'none', 'tired')): 0.7,
                ((True, False, False), ('none', 'none', 'exhausted')): 0.3,
            }
        elif a[0] == 'rest' and a[1] == 'stay' and a[2] == 'go':
            return {
                ((True, True, False), ('none', 'none', 'frustrated')): 1.0,
            }
        elif a[0] == 'rest' and a[1] == 'go' and a[2] == 'rest':
            return {
                ((True, False, True), ('none', 'none', 'relieved')): 1.0,
            }
        elif a[0] == 'accompany' and a[1] == 'stay' and a[2] == 'go':
            return {
                ((True, True, False), ('none', 'none', 'frustrated')): 1.0,
            }
        elif a[0] == 'accompany' and a[1] == 'go' and a[2] == 'rest':
            return {
                ((True, False, True), ('none', 'none', 'relieved')): 1.0,
            }
        elif a[0] == 'rest' and a[1] == 'stay' and a[2] == 'rest':
            return {
                ((True, True, True), ('none', 'none', 'none')): 1.0,
            }
        elif a[0] == 'accompany' and a[1] == 'stay' and a[2] == 'rest':
            return {
                ((True, True, True), ('none', 'none', 'none')): 1.0,
            }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
