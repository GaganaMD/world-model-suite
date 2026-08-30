from posg import POSG

class FlightWarningPOSG(POSG):
    """Player 0 is the robot copilot; player 1 is the human pilot.

    State coordinates are:
    (message_condition, pilot_condition, interaction_condition).

    The pilot condition is settled only after the robot receives the private
    warning. The interaction ends with that receipt because no subsequent act
    by the robot or pilot is specified.
    """

    n_players = 2

    def initial_distribution(self):
        state = ("pending", "undetermined", "open")
        observations = ("none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s[2] == "ended"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("receive_message",)
        return ("noop",)

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}

        planning = ("received", "planning", "ended")
        not_planning = ("received", "not_planning", "ended")
        observations = ("private_warning", "none")
        return {
            (planning, observations): 0.5,
            (not_planning, observations): 0.5,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
