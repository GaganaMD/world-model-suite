from posg import POSG

class RobotTeacherPOSG(POSG):
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {
            ((False, False), ('none', 'none', 'none')): 0.5,
            ((True, False), ('giggle', 'protest', 'none')): 0.5,
        }

    def is_terminal(self, s: S) -> bool:
        return s[0][0] and s[0][1]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:
            return ('apologize', 'defend', 'ignore')
        elif i == 1:
            return ('giggle', 'protest', 'none')
        else:
            return ('protest', 'none')

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'apologize':
            return {
                ((True, True), ('apology', 'none', 'none')): 1.0,
            }
        elif a[0] == 'defend':
            return {
                ((False, False), ('defence', 'protest', 'none')): 0.6,
                ((False, False), ('defence', 'none', 'protest')): 0.4,
            }
        elif a[0] == 'ignore':
            return {
                ((False, False), ('none', 'protest', 'none')): 1.0,
            }
        else:
            return {
                ((False, False), ('none', 'none', 'none')): 1.0,
            }

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0, 0.0)
