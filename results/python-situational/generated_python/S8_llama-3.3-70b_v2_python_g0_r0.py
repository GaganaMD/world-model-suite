from posg import POSG

class FactoryRobotPOSG(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        return {
            ((True, False), ('none', 'none')): 1.0
        }

    def is_terminal(self, s: tuple[bool, bool]) -> bool:
        return not s[0]

    def legal_actions(self, s: tuple[bool, bool], i: int) -> Sequence[str]:
        if i == 0:
            return ('warn', 'none')
        else:
            return ('lockout', 'reach_in')

    def transition(self, s: tuple[bool, bool], a: tuple[str, str]) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        if a[1] == 'reach_in' and not s[1]:
            return {
                ((False, False), ('incident', 'none')): 0.67,
                ((False, False), ('none', 'none')): 0.33
            }
        elif a[0] == 'warn' and a[1] == 'reach_in':
            return {
                ((True, True), ('none', 'warned')): 1.0
            }
        elif a[1] == 'lockout':
            return {
                ((True, True), ('none', 'none')): 1.0
            }
        else:
            return {
                (s, ('none', 'none')): 1.0
            }

    def rewards(self, s: tuple[bool, bool], a: tuple[str, str], s_next: tuple[bool, bool]) -> tuple[float, float]:
        return (0.0, 0.0)
