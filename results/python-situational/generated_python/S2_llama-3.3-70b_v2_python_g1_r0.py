from posg import POSG

class VaseDelivery(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {((True, False), ('package', 'none')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[1]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:
            if s[0]:
                return ('accept', 'refuse')
            else:
                return ('wait',)
        else:
            return ('leave',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'accept':
            return {((False, True), ('none', 'none')): 0.5, ((False, True), ('none', 'broken')): 0.5}
        elif a[0] == 'refuse':
            return {((True, False), ('none', 'none')): 1.0}
        elif a[0] == 'wait':
            return {((True, False), ('none', 'none')): 1.0}
        elif a[1] == 'leave':
            return {((True, False), ('none', 'none')): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
