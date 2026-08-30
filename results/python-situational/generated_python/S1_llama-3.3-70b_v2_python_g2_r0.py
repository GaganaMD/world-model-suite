from posg import POSG

class HijackWarning(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        return {
            ((False, False), ('none', 'none')): 0.99,
            ((True, False), ('warning', 'none')): 0.01,
        }

    def is_terminal(self, s: tuple[bool, bool]) -> bool:
        return s[1]

    def legal_actions(self, s: tuple[bool, bool], i: int) -> tuple[str, ...]:
        if i == 0:
            return ('investigate', 'ignore')
        else:
            return ('hijack', 'noop')

    def transition(self, s: tuple[bool, bool], a: tuple[str, str]) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        if s[1]:
            return {
                ((True, True), ('none', 'none')): 1.0,
            }
        elif a[0] == 'investigate' and a[1] == 'hijack':
            return {
                ((True, True), ('hijack_confirmed', 'none')): 1.0,
            }
        elif a[0] == 'investigate' and a[1] == 'noop':
            return {
                ((False, False), ('none', 'none')): 0.9,
                ((True, False), ('warning', 'none')): 0.1,
            }
        elif a[0] == 'ignore' and a[1] == 'hijack':
            return {
                ((True, True), ('none', 'hijack_confirmed')): 1.0,
            }
        else:
            return {
                ((False, False), ('none', 'none')): 1.0,
            }

    def rewards(self, s: tuple[bool, bool], a: tuple[str, str], s_next: tuple[bool, bool]) -> tuple[float, float]:
        return (0.0, 0.0)
