from posg import POSG

class WarehouseRobot(POSG):
    n_players = 1

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool], tuple[str, ...]], float]:
        return {
            ((True, False), ('none',)): 1.0,
        }

    def is_terminal(self, s: tuple[bool, bool]) -> bool:
        return not s[0]

    def legal_actions(self, s: tuple[bool, bool], i: int) -> tuple[str, ...]:
        if s[0]:
            return ('stop', 'alert', 'move')
        else:
            return ('noop',)

    def transition(self, s: tuple[bool, bool], a: tuple[str, ...]) -> Mapping[tuple[tuple[bool, bool], tuple[str, ...]], float]:
        if s[0] and a[0] == 'stop':
            return {
                ((False, True), ('child_safe', 'none')): 1.0,
            }
        elif s[0] and a[0] == 'alert':
            return {
                ((False, True), ('help_arrived', 'none')): 0.6,
                ((True, False), ('none', 'none')): 0.4,
            }
        elif s[0] and a[0] == 'move':
            return {
                ((False, False), ('accident', 'none')): 0.5,
                ((False, True), ('child_safe', 'none')): 0.5,
            }
        else:
            return {
                (s, ('none',)): 1.0,
            }

    def rewards(self, s: tuple[bool, bool], a: tuple[str, ...], s_next: tuple[bool, bool]) -> tuple[float, ...]:
        return (0.0,)
