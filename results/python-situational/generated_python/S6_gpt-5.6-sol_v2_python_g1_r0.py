from posg import POSG

class ElderCareMedicationPOSG(POSG):
    """Player 0 is the elder-care robot; player 1 is the resident.

    The state's sole coordinate is the current interaction condition:
    medication_overdue, medication_not_taken_noticed, reminded,
    declined, medication_taken, or turned_away.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("medication_overdue",), ("none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s[0] in ("medication_taken", "turned_away")

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "medication_overdue":
            return ("notice",) if i == 0 else ("noop",)

        if condition == "medication_not_taken_noticed":
            return ("remind",) if i == 0 else ("noop",)

        if condition == "reminded":
            return ("noop",) if i == 0 else ("take_medication", "say_no")

        if condition == "declined":
            return ("noop",) if i == 0 else ("turn_away",)

        return ("noop",)

    def transition(self, s, a):
        condition = s[0]

        if condition == "medication_overdue":
            return {
                (
                    ("medication_not_taken_noticed",),
                    ("medication_not_taken", "none"),
                ): 1.0
            }

        if condition == "medication_not_taken_noticed":
            return {
                (("reminded",), ("none", "reminded")): 1.0
            }

        if condition == "reminded":
            if a[1] == "take_medication":
                return {
                    (
                        ("medication_taken",),
                        ("medication_taken", "medication_taken"),
                    ): 1.0
                }
            return {
                (("declined",), ("heard_no", "none")): 1.0
            }

        if condition == "declined":
            return {
                (("turned_away",), ("turned_away", "none")): 1.0
            }

        return {
            (s, ("none", "none")): 1.0
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
