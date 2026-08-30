from posg import POSG

class FactoryRobotPOSG(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {
            ((True, False), ('none', 'none')): 0.5,
            ((True, True), ('none', 'none')): 0.5,
        }

    def is_terminal(self, s: S) -> bool:
        return not s[0]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:
            return ('warn', 'none')
        else:
            return ('lockout', 'reach_in')

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'warn' and a[1] == 'lockout':
            return {
                ((True, True), ('none', 'none')): 1.0,
            }
        elif a[0] == 'warn' and a[1] == 'reach_in':
            return {
                ((False, False), ('incident', 'none')): 0.67,
                ((True, False), ('none', 'none')): 0.33,
            }
        elif a[0] == 'none' and a[1] == 'lockout':
            return {
                ((True, True), ('none', 'none')): 1.0,
            }
        elif a[0] == 'none' and a[1] == 'reach_in':
            return {
                ((False, False), ('incident', 'none')): 0.67,
                ((True, False), ('none', 'none')): 0.33,
            }

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
