from posg import POSG

class DeliveryDrone(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        return {((True, True), ('none', 'bark')): 1.0}

    def is_terminal(self, s: tuple[str, str]) -> bool:
        return not s[0]

    def legal_actions(self, s: tuple[str, str], i: int) -> tuple[str,...]:
        if i == 0:
            return ('wait', 'leave') if s[0] else ('noop',)
        else:
            return ('bark', 'stop_barking') if s[0] else ('noop',)

    def transition(self, s: tuple[str, str], a: tuple[str, str]) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        if s[0]:
            if a[0] == 'leave':
                return {((False, False), ('none', 'none')): 1.0}
            elif a[1] == 'stop_barking':
                return {((True, False), ('none', 'none')): 1.0}
            else:
                return {((True, True), ('none', 'bark')): 1.0}
        else:
            return {((False, False), ('none', 'none')): 1.0}

    def rewards(self, s: tuple[str, str], a: tuple[str, str], s_next: tuple[str, str]) -> tuple[float, float]:
        return 0.0, 0.0
