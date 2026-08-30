from posg import POSG

class ElderCareMedicationPOSG(POSG):
    """Player a[0] is the elder-care robot; player a[1] is the resident.
    The state tuple contains the current medication-interaction condition.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("medication_overdue",), ("none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("resident_turned_away",)

    def legal_actions(self, s, i):
        if s == ("medication_overdue",):
            return ("notice",) if i == 0 else ("noop",)
        if s == ("robot_aware",):
            return ("remind",) if i == 0 else ("noop",)
        if s == ("resident_reminded",):
            return ("noop",) if i == 0 else ("say_do_not_want_it",)
        if s == ("resident_spoke",):
            return ("noop",) if i == 0 else ("turn_away",)
        if s == ("resident_turned_away",):
            return ("noop",)
        raise ValueError("unknown state")

    def transition(self, s, a):
        if s == ("medication_overdue",) and a == ("notice", "noop"):
            return {
                (("robot_aware",), ("medication_overdue", "none")): 1.0
            }
        if s == ("robot_aware",) and a == ("remind", "noop"):
            return {
                (("resident_reminded",), ("none", "reminded")): 1.0
            }
        if s == ("resident_reminded",) and a == ("noop", "say_do_not_want_it"):
            return {
                (("resident_spoke",), ("do_not_want_medication", "none")): 1.0
            }
        if s == ("resident_spoke",) and a == ("noop", "turn_away"):
            return {
                (("resident_turned_away",), ("turned_away", "none")): 1.0
            }
        if s == ("resident_turned_away",) and a == ("noop", "noop"):
            return {
                (("resident_turned_away",), ("none", "none")): 1.0
            }
        raise ValueError("illegal action profile")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
