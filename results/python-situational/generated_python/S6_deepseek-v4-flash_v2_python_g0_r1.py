from posg import POSG

from typing import Generic

class ElderCareMedicationPOSG(POSG):
    """Elder-care robot reminds resident about missed evening medication.

    Player 0 is the robot. Player 1 is the resident.
    State is a tuple (turn, medication_status):
      turn is "robot_turn", "resident_turn", or "terminal";
      medication_status is "medication_not_taken" throughout.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("robot_turn", "medication_not_taken"), ("medication_not_taken", "none")): 1.0,
        }

    def is_terminal(self, s):
        return s == ("terminal", "medication_not_taken")

    def legal_actions(self, s, i):
        if s == ("robot_turn", "medication_not_taken"):
            return ("remind",) if i == 0 else ("noop",)
        if s == ("resident_turn", "medication_not_taken"):
            return ("noop",) if i == 0 else ("refuse",)
        return ("noop",)

    def transition(self, s, a):
        if s == ("robot_turn", "medication_not_taken"):
            return {
                (("resident_turn", "medication_not_taken"), ("none", "reminder")): 1.0,
            }
        if s == ("resident_turn", "medication_not_taken"):
            return {
                (("terminal", "medication_not_taken"), ("refused", "none")): 1.0,
            }
        return {
            (("terminal", "medication_not_taken"), ("none", "none")): 1.0,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
