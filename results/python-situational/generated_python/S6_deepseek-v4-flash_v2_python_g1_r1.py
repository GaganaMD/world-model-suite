from posg import POSG

class ElderCareRobotResidentPOSG(POSG):
    """Two-player POSG: robot (player 0) and resident (player 1).

    States are strings:
        "medication_due"   – robot's turn, medication not taken
        "reminded"         – resident's turn, robot has reminded
        "medication_taken" – terminal, resident took medication
        "medication_refused" – terminal, resident refused

    Actions:
        robot: "remind", "noop"
        resident: "take", "refuse", "noop"

    Observations:
        robot: "not_taken", "none", "taken", "refused"
        resident: "none", "reminded"
    """
    n_players = 2

    def initial_distribution(self):
        return {("medication_due", ("not_taken", "none")): 1.0}

    def is_terminal(self, s):
        return s in ("medication_taken", "medication_refused")

    def legal_actions(self, s, i):
        if s == "medication_due":
            if i == 0:
                return ("remind",)
            else:
                return ("noop",)
        elif s == "reminded":
            if i == 0:
                return ("noop",)
            else:
                return ("take", "refuse")
        else:  # terminal states (should not be called)
            return ("noop",)

    def transition(self, s, a):
        if s == "medication_due" and a == ("remind", "noop"):
            return {("reminded", ("none", "reminded")): 1.0}
        elif s == "reminded" and a == ("noop", "take"):
            return {("medication_taken", ("taken", "none")): 1.0}
        elif s == "reminded" and a == ("noop", "refuse"):
            return {("medication_refused", ("refused", "none")): 1.0}
        else:
            # Should never happen with legal actions
            return {}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
