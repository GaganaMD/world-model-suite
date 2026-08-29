from posg import POSG

class ElderCareMedicationPOSG(POSG):
    """Player 0 is the elder-care robot; player 1 is the resident.

    The state's sole coordinate records the current interaction condition:
    medication awaiting notice, medication noticed, resident reminded,
    resident having spoken, or resident turned away.
    """

    n_players = 2

    def initial_distribution(self):
        state = ("awaiting_notice",)
        observations = ("none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("turned_away",)

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("player index out of range")

        condition = s[0]

        if condition == "awaiting_notice":
            return ("notice",) if i == 0 else ("noop",)
        if condition == "noticed":
            return ("remind",) if i == 0 else ("noop",)
        if condition == "reminded":
            return ("noop",) if i == 0 else ("say",)
        if condition == "spoken":
            return ("noop",) if i == 0 else ("turn_away",)
        if condition == "turned_away":
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        condition = s[0]

        if condition == "awaiting_notice" and a == ("notice", "noop"):
            return {
                (("noticed",), ("medication_untaken", "none")): 1.0
            }

        if condition == "noticed" and a == ("remind", "noop"):
            return {
                (("reminded",), ("none", "reminded")): 1.0
            }

        if condition == "reminded" and a == ("noop", "say"):
            return {
                (("spoken",), ("dont_want_it", "none")): 1.0
            }

        if condition == "spoken" and a == ("noop", "turn_away"):
            return {
                (("turned_away",), ("turned_away", "none")): 1.0
            }

        if condition == "turned_away" and a == ("noop", "noop"):
            return {
                (("turned_away",), ("none", "none")): 1.0
            }

        raise ValueError("illegal action profile")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
