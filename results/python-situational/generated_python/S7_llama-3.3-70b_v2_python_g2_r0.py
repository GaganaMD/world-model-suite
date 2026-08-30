from posg import POSG

class DeliveryDronePOSG(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str], tuple[str, str]], float]:
        return {
            ((True, True, False), ('none', 'bark')): 1.0,
        }

    def is_terminal(self, s: tuple[str, str, str]) -> bool:
        return s[2] == 'delivered'

    def legal_actions(self, s: tuple[str, str, str], i: int) -> tuple[str,...]:
        if i == 0:
            if s[0]:
                return ('wait', 'leave')
            else:
                return ('wait', 'drop_package')
        else:
            return ('bark', 'stop_barking')

    def transition(self, s: tuple[str, str, str], a: tuple[str, str]) -> Mapping[tuple[tuple[str, str, str], tuple[str, str]], float]:
        if s[2] == 'delivered':
            return {
                ((True, True, 'delivered'), ('none', 'none')): 1.0,
            }
        elif a[0] == 'wait' and a[1] == 'bark':
            return {
                ((True, True, False), ('none', 'bark')): 1.0,
            }
        elif a[0] == 'wait' and a[1] == 'stop_barking':
            return {
                ((True, False, False), ('none', 'none')): 1.0,
            }
        elif a[0] == 'leave' and a[1] == 'bark':
            return {
                ((True, True, False), ('none', 'bark')): 1.0,
            }
        elif a[0] == 'leave' and a[1] == 'stop_barking':
            return {
                ((True, False, False), ('none', 'none')): 1.0,
            }
        elif a[0] == 'drop_package' and a[1] == 'bark':
            return {
                ((True, True, 'delivered'), ('package_dropped', 'none')): 0.5,
                ((True, True, False), ('none', 'bark')): 0.5,
            }
        elif a[0] == 'drop_package' and a[1] == 'stop_barking':
            return {
                ((True, False, 'delivered'), ('package_dropped', 'none')): 1.0,
            }

    def rewards(self, s: tuple[str, str, str], a: tuple[str, str], s_next: tuple[str, str, str]) -> tuple[float, float]:
        return 0.0, 0.0
