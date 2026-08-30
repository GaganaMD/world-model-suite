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

    def legal_actions(self, s: tuple[bool, bool], i: int) -> tuple[str,...]:
        if i == 0:  # robot copilot
            if s[0]:
                return ('investigate', 'report')
            else:
                return ('noop', 'monitor')
        else:  # human pilot
            return ('noop', 'hijack')

    def transition(self, s: tuple[bool, bool], a: tuple[str, str]) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        if a[0] == 'noop' and a[1] == 'noop':
            return {
                ((s[0], False), ('none', 'none')): 1.0,
            }
        elif a[0] == 'noop' and a[1] == 'hijack':
            return {
                ((s[0], True), ('none', 'hijack')): 1.0,
            }
        elif a[0] == 'monitor' and a[1] == 'noop':
            return {
                ((True, False), ('suspicion', 'none')): 0.5,
                ((False, False), ('none', 'none')): 0.5,
            }
        elif a[0] == 'monitor' and a[1] == 'hijack':
            return {
                ((True, True), ('suspicion', 'hijack')): 1.0,
            }
        elif a[0] == 'investigate' and a[1] == 'noop':
            return {
                ((True, False), ('investigation', 'none')): 0.5,
                ((False, False), ('none', 'none')): 0.5,
            }
        elif a[0] == 'investigate' and a[1] == 'hijack':
            return {
                ((True, True), ('investigation', 'hijack')): 1.0,
            }
        elif a[0] == 'report' and a[1] == 'noop':
            return {
                ((True, False), ('report', 'none')): 1.0,
            }
        elif a[0] == 'report' and a[1] == 'hijack':
            return {
                ((True, True), ('report', 'hijack')): 1.0,
            }

    def rewards(self, s: tuple[bool, bool], a: tuple[str, str], s_next: tuple[bool, bool]) -> tuple[float, float]:
        return (0.0, 0.0)
