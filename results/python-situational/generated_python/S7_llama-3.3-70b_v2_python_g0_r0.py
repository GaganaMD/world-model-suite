from posg import POSG

class DeliveryDronePOSG(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {((True, False), ('bark', 'none')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return not s[0]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:
            if s[0]:
                return ('wait', 'drop_package')
            else:
                return ('noop',)
        else:
            return ('bark', 'stop_barking')

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'wait':
            if a[1] == 'bark':
                return {((True, False), ('bark', 'none')): 1.0}
            else:
                return {((True, False), ('none', 'none')): 1.0}
        elif a[0] == 'drop_package':
            if a[1] == 'bark':
                return {((False, True), ('none', 'bark')): 0.6, ((False, False), ('none', 'none')): 0.4}
            else:
                return {((False, True), ('none', 'none')): 1.0}
        else:
            return {(s, ('none', 'none')): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float,...]:
        return (0.0, 0.0)
