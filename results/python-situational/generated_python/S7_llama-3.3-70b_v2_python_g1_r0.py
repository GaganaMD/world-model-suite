from posg import POSG

class DeliveryDronePOSG(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {((True, False), ('none', 'drone')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return not s[0]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:
            return ('wait', 'drop_package') if s[0] else ('noop',)
        else:
            return ('bark', 'stop_barking') if s[0] else ('noop',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'wait' and a[1] == 'bark':
            return {((True, False), ('none', 'drone')): 1.0}
        elif a[0] == 'wait' and a[1] == 'stop_barking':
            return {((True, True), ('none', 'quiet')): 1.0}
        elif a[0] == 'drop_package' and a[1] == 'bark':
            return {((False, False), ('package_dropped', 'drone')): 1.0}
        elif a[0] == 'drop_package' and a[1] == 'stop_barking':
            return {((False, True), ('package_dropped', 'quiet')): 1.0}
        else:
            return {(s, ('none', 'none')): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float,...]:
        return (0.0, 0.0)
