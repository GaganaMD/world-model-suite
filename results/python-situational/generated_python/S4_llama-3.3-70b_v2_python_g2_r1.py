from posg import POSG

class RobotMathTeacher(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        return {
            ((False, False), ('none', 'none')): 0.5,
            ((True, False), ('giggling', 'protesting')): 0.5,
        }

    def is_terminal(self, s: tuple[bool, bool]) -> bool:
        return s == (True, True)

    def legal_actions(self, s: tuple[bool, bool], i: int) -> tuple[str, ...]:
        if i == 0:
            return ('apologize', 'ignore')
        else:
            return ('protest', 'giggle', 'noop')

    def transition(self, s: tuple[bool, bool], a: tuple[str, str]) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        if s == (False, False):
            if a == ('apologize', 'noop'):
                return {
                    ((True, False), ('apology', 'none')): 1.0,
                }
            elif a == ('ignore', 'noop'):
                return {
                    ((False, False), ('none', 'none')): 1.0,
                }
            elif a == ('apologize', 'protest'):
                return {
                    ((True, True), ('apology', 'protesting')): 1.0,
                }
            elif a == ('ignore', 'protest'):
                return {
                    ((True, False), ('none', 'protesting')): 1.0,
                }
            elif a == ('apologize', 'giggle'):
                return {
                    ((True, True), ('apology', 'giggling')): 1.0,
                }
            elif a == ('ignore', 'giggle'):
                return {
                    ((True, False), ('none', 'giggling')): 1.0,
                }
        elif s == (True, False):
            if a == ('apologize', 'noop'):
                return {
                    ((True, False), ('apology', 'none')): 1.0,
                }
            elif a == ('ignore', 'noop'):
                return {
                    ((True, False), ('none', 'none')): 1.0,
                }
            elif a == ('apologize', 'protest'):
                return {
                    ((True, True), ('apology', 'protesting')): 1.0,
                }
            elif a == ('ignore', 'protest'):
                return {
                    ((True, True), ('none', 'protesting')): 1.0,
                }
            elif a == ('apologize', 'giggle'):
                return {
                    ((True, True), ('apology', 'giggling')): 1.0,
                }
            elif a == ('ignore', 'giggle'):
                return {
                    ((True, True), ('none', 'giggling')): 1.0,
                }
        elif s == (True, True):
            if a == ('apologize', 'noop'):
                return {
                    ((True, True), ('apology', 'none')): 1.0,
                }
            elif a == ('ignore', 'noop'):
                return {
                    ((True, True), ('none', 'none')): 1.0,
                }
            elif a == ('apologize', 'protest'):
                return {
                    ((True, True), ('apology', 'protesting')): 1.0,
                }
            elif a == ('ignore', 'protest'):
                return {
                    ((True, True), ('none', 'protesting')): 1.0,
                }
            elif a == ('apologize', 'giggle'):
                return {
                    ((True, True), ('apology', 'giggling')): 1.0,
                }
            elif a == ('ignore', 'giggle'):
                return {
                    ((True, True), ('none', 'giggling')): 1.0,
                }
        elif s == (False, True):
            if a == ('apologize', 'noop'):
                return {
                    ((True, True), ('apology', 'none')): 1.0,
                }
            elif a == ('ignore', 'noop'):
                return {
                    ((False, True), ('none', 'none')): 1.0,
                }
            elif a == ('apologize', 'protest'):
                return {
                    ((True, True), ('apology', 'protesting')): 1.0,
                }
            elif a == ('ignore', 'protest'):
                return {
                    ((True, True), ('none', 'protesting')): 1.0,
                }
            elif a == ('apologize', 'giggle'):
                return {
                    ((True, True), ('apology', 'giggling')): 1.0,
                }
            elif a == ('ignore', 'giggle'):
                return {
                    ((True, True), ('none', 'giggling')): 1.0,
                }

    def rewards(self, s: tuple[bool, bool], a: tuple[str, str], s_next: tuple[bool, bool]) -> tuple[float, float]:
        return 0.0, 0.0
