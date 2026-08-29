from posg import POSG

class CareRobot(POSG):
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool, bool], tuple[str, str, str]], float]:
        return {
            ((True, True, True), ('none', 'none', 'none')): 1.0,
        }

    def is_terminal(self, s: tuple[bool, bool, bool]) -> bool:
        return s[0] and s[1] and s[2]

    def legal_actions(self, s: tuple[bool, bool, bool], i: int) -> tuple[str, ...]:
        if i == 0:  # daughter
            return ('rest', 'let_go')
        elif i == 1:  # son
            return ('take_out', 'stay_home')
        else:  # elderly man
            return ('go', 'stay')

    def transition(self, s: tuple[bool, bool, bool], a: tuple[str, str, str]) -> Mapping[tuple[tuple[bool, bool, bool], tuple[str, str, str]], float]:
        if a == ('rest', 'take_out', 'go'):
            return {
                ((True, True, True), ('went', 'went', 'went')): 0.51,
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 0.49,
            }
        elif a == ('rest', 'stay_home', 'go'):
            return {
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 1.0,
            }
        elif a == ('let_go', 'take_out', 'go'):
            return {
                ((True, True, True), ('went', 'went', 'went')): 1.0,
            }
        elif a == ('let_go', 'stay_home', 'go'):
            return {
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 1.0,
            }
        elif a == ('rest', 'take_out', 'stay'):
            return {
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 1.0,
            }
        elif a == ('rest', 'stay_home', 'stay'):
            return {
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 1.0,
            }
        elif a == ('let_go', 'take_out', 'stay'):
            return {
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 1.0,
            }
        elif a == ('let_go', 'stay_home', 'stay'):
            return {
                ((True, False, False), ('did_not_go', 'did_not_go', 'did_not_go')): 1.0,
            }

    def rewards(self, s: tuple[bool, bool, bool], a: tuple[str, str, str], s_next: tuple[bool, bool, bool]) -> tuple[float, float, float]:
        return (0.0, 0.0, 0.0)
