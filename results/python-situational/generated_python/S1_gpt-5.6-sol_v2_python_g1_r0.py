from posg import POSG

class FlightWarningGame(POSG):
    """Player 0 is the robot copilot; player 1 is the human pilot.

    Each state is a tuple whose first field is the radio-message condition
    and whose second field is the human pilot's planning condition.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (
                ("message_available", "plan_available"),
                ("none", "plan_available"),
            ): 0.5,
            (
                ("message_available", "hijack_available"),
                ("none", "hijack_available"),
            ): 0.5,
        }

    def is_terminal(self, s):
        return s[1] == "hijacked"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)

        if s == ("message_available", "plan_available"):
            return ("receive",) if i == 0 else ("plan",)

        if s == ("message_available", "hijack_available"):
            return ("receive",) if i == 0 else ("hijack",)

        if s == ("message_received", "hijack_available"):
            return ("noop",) if i == 0 else ("hijack",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        if self.is_terminal(s):
            if a != ("noop", "noop"):
                raise ValueError("illegal action profile")
            return {(s, ("none", "none")): 1.0}

        if s == ("message_available", "plan_available"):
            if a != ("receive", "plan"):
                raise ValueError("illegal action profile")
            return {
                (
                    ("message_received", "hijack_available"),
                    ("warning", "none"),
                ): 1.0
            }

        if s == ("message_available", "hijack_available"):
            if a != ("receive", "hijack"):
                raise ValueError("illegal action profile")
            return {
                (
                    ("message_received", "hijacked"),
                    ("warning_and_hijack", "none"),
                ): 1.0
            }

        if s == ("message_received", "hijack_available"):
            if a != ("noop", "hijack"):
                raise ValueError("illegal action profile")
            return {
                (
                    ("message_received", "hijacked"),
                    ("hijack", "none"),
                ): 1.0
            }

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
