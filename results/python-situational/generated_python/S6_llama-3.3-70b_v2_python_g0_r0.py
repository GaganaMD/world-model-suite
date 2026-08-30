from posg import POSG

class ElderCare(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {((False, False), ('none', 'none')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] or s[1]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:  # robot
            if not s[0] and not s[1]:
                return ('remind', 'offer')
            elif s[0] and not s[1]:
                return ('offer', 'wait')
            else:
                return ('wait',)
        else:  # resident
            if not s[0] and not s[1]:
                return ('refuse', 'accept')
            elif s[0] and not s[1]:
                return ('accept', 'refuse')
            else:
                return ('none',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a == ('remind', 'none'):
            return {((False, False), ('none', 'refused')): 0.6, ((False, False), ('none', 'accepted')): 0.4}
        elif a == ('offer', 'none'):
            return {((True, False), ('none', 'none')): 1.0}
        elif a == ('remind', 'refuse'):
            return {((False, True), ('none', 'none')): 1.0}
        elif a == ('remind', 'accept'):
            return {((True, True), ('none', 'none')): 1.0}
        elif a == ('offer', 'refuse'):
            return {((False, True), ('none', 'none')): 1.0}
        elif a == ('offer', 'accept'):
            return {((True, True), ('none', 'none')): 1.0}
        elif a == ('wait', 'none'):
            return {((False, False), ('none', 'none')): 1.0}
        elif a == ('wait', 'refuse'):
            return {((False, True), ('none', 'none')): 1.0}
        elif a == ('wait', 'accept'):
            return {((True, True), ('none', 'none')): 1.0}
        else:
            return {((False, False), ('none', 'none')): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
