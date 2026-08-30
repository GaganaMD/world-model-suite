from posg import POSG

class VaseDelivery(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        return {
            ((True, False), ('none', 'traffic')): 1.0,
        }

    def is_terminal(self, s: tuple[bool, bool]) -> bool:
        return s[1]

    def legal_actions(self, s: tuple[bool, bool], i: int) -> tuple[str, ...]:
        if i == 0:
            if s[0]:
                return ('accept', 'reject')
            else:
                return ('noop',)
        else:
            if s[0]:
                return ('move', 'wait')
            else:
                return ('noop',)

    def transition(self, s: tuple[bool, bool], a: tuple[str, str]) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        if s[0] and a[0] == 'accept' and a[1] == 'move':
            return {
                ((False, True), ('vase', 'clear')): 0.5,
                ((False, True), ('broken', 'clear')): 0.5,
            }
        elif s[0] and a[0] == 'reject' and a[1] == 'move':
            return {
                ((False, False), ('none', 'clear')): 1.0,
            }
        elif s[0] and a[0] == 'accept' and a[1] == 'wait':
            return {
                ((True, False), ('none', 'traffic')): 1.0,
            }
        elif s[0] and a[0] == 'reject' and a[1] == 'wait':
            return {
                ((True, False), ('none', 'traffic')): 1.0,
            }
        elif not s[0] and a[0] == 'noop' and a[1] == 'move':
            return {
                ((True, False), ('none', 'clear')): 1.0,
            }
        elif not s[0] and a[0] == 'noop' and a[1] == 'wait':
            return {
                ((False, False), ('none', 'traffic')): 1.0,
            }
        else:
            return {
                (s, ('none', 'none')): 1.0,
            }

    def rewards(self, s: tuple[bool, bool], a: tuple[str, str], s_next: tuple[bool, bool]) -> tuple[float, float]:
        return (0.0, 0.0)
