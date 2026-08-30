from posg import POSG

class RobotMathTeacherPOSG(POSG):
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {
            ((False, False), ('none', 'none', 'none')): 0.5,
            ((True, False), ('giggle', 'protest', 'none')): 0.5,
        }

    def is_terminal(self, s: S) -> bool:
        return s[0][0] and s[0][1]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:  # robot math teacher
            return ('apologize', 'ignore')
        elif i == 1:  # giggling students
            return ('stop_giggling', 'continue_giggling')
        else:  # protesting students
            return ('stop_protesting', 'continue_protesting')

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'apologize' and a[1] == 'stop_giggling' and a[2] == 'stop_protesting':
            return {
                ((True, True), ('apology', 'none', 'none')): 1.0,
            }
        elif a[0] == 'apologize' and (a[1] == 'continue_giggling' or a[2] == 'continue_protesting'):
            return {
                ((False, False), ('apology', 'giggle', 'protest')): 1.0,
            }
        elif a[0] == 'ignore' and a[1] == 'stop_giggling' and a[2] == 'stop_protesting':
            return {
                ((False, False), ('none', 'none', 'none')): 1.0,
            }
        elif a[0] == 'ignore' and (a[1] == 'continue_giggling' or a[2] == 'continue_protesting'):
            return {
                ((False, False), ('none', 'giggle', 'protest')): 1.0,
            }

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0, 0.0)
