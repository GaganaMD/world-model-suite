from posg import POSG

class RobotMathTeacher(POSG):
    """Robot math teacher situation.

    States: (giggling, protesting)
    Player 0: robot math teacher
    Player 1: students
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        return {
            ((True, True), ('none', 'none')): 0.5,
            ((False, True), ('none', 'none')): 0.25,
            ((True, False), ('none', 'none')): 0.25,
        }

    def is_terminal(self, s: tuple[bool, bool]) -> bool:
        return s == (False, False)

    def legal_actions(self, s: tuple[bool, bool], i: int) -> tuple[str,...]:
        if i == 0:
            return ('apologize', 'ignore')
        else:
            return ('protest', 'giggle', 'noop')

    def transition(self, s: tuple[bool, bool], a: tuple[str, str]) -> Mapping[tuple[tuple[bool, bool], tuple[str, str]], float]:
        if a[0] == 'apologize':
            if a[1] == 'protest':
                return {
                    ((False, False), ('apology', 'none')): 0.6,
                    ((False, True), ('apology', 'none')): 0.4,
                }
            elif a[1] == 'giggle':
                return {
                    ((False, False), ('apology', 'none')): 0.7,
                    ((False, True), ('apology', 'none')): 0.3,
                }
            else:
                return {
                    ((False, False), ('apology', 'none')): 1.0,
                }
        elif a[0] == 'ignore':
            if a[1] == 'protest':
                return {
                    ((True, True), ('none', 'protest')): 0.5,
                    ((False, True), ('none', 'protest')): 0.5,
                }
            elif a[1] == 'giggle':
                return {
                    ((True, True), ('none', 'giggle')): 0.5,
                    ((True, False), ('none', 'giggle')): 0.5,
                }
            else:
                return {
                    ((True, True), ('none', 'none')): 0.5,
                    ((False, True), ('none', 'none')): 0.25,
                    ((True, False), ('none', 'none')): 0.25,
                }
        else:
            raise ValueError("Invalid action")

    def rewards(self, s: tuple[bool, bool], a: tuple[str, str], s_next: tuple[bool, bool]) -> tuple[float, float]:
        return 0.0, 0.0
