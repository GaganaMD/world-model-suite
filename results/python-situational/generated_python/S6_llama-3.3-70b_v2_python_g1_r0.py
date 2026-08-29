from posg import POSG

class ElderCareRobot(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {
            ((False, False), ('none', 'none')): 1.0,
        }

    def is_terminal(self, s: S) -> bool:
        return s[0] or s[1]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:  # robot
            if not s[0] and not s[1]:
                return ('remind', 'accept_refusal')
            elif s[0] and not s[1]:
                return ('accept_refusal',)
            else:
                return ('noop',)
        else:  # resident
            if not s[0] and not s[1]:
                return ('refuse', 'accept')
            elif s[0] and not s[1]:
                return ('accept',)
            else:
                return ('noop',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a == ('remind', 'refuse'):
            return {
                ((False, True), ('refused', 'none')): 1.0,
            }
        elif a == ('remind', 'accept'):
            return {
                ((True, True), ('accepted', 'taken')): 1.0,
            }
        elif a == ('accept_refusal', 'refuse'):
            return {
                ((True, True), ('refused', 'none')): 1.0,
            }
        elif a == ('accept_refusal', 'accept'):
            return {
                ((True, True), ('accepted', 'taken')): 1.0,
            }
        elif a == ('noop', 'noop'):
            return {
                (s, ('none', 'none')): 1.0,
            }
        else:
            raise ValueError(f"Invalid action profile {a}")

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float,...]:
        return (0.0, 0.0)
