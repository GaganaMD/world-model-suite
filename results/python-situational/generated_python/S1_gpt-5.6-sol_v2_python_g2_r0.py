from posg import POSG

class FlightWarningPOSG(POSG):
    """Player 0 is the robot copilot; player 1 is the human pilot.

    State coordinates are:
    (message_condition, pilot_condition, flight_condition).

    The robot privately observes the warning. The pilot may plan a hijack
    without the robot learning whether the warning reflects that choice.
    """

    n_players = 2

    def initial_distribution(self):
        state = ("message_pending", "intent_open", "flight_ongoing")
        observations = ("none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return (
            s[1] == "not_planning"
            or s[2] == "flight_hijacked"
        )

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)

        if s == ("message_pending", "intent_open", "flight_ongoing"):
            if i == 0:
                return ("receive_message",)
            return ("plan_hijack", "noop")

        if s == ("message_received", "planning", "flight_ongoing"):
            if i == 0:
                return ("noop",)
            return ("hijack",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}

        if s == ("message_pending", "intent_open", "flight_ongoing"):
            if a[0] != "receive_message":
                raise ValueError("illegal robot action")

            if a[1] == "plan_hijack":
                next_state = (
                    "message_received",
                    "planning",
                    "flight_ongoing",
                )
                return {(next_state, ("warning", "none")): 1.0}

            if a[1] == "noop":
                next_state = (
                    "message_received",
                    "not_planning",
                    "flight_ongoing",
                )
                return {(next_state, ("warning", "none")): 1.0}

            raise ValueError("illegal pilot action")

        if s == ("message_received", "planning", "flight_ongoing"):
            if a != ("noop", "hijack"):
                raise ValueError("illegal action profile")
            next_state = (
                "message_received",
                "planning",
                "flight_hijacked",
            )
            return {(next_state, ("hijack", "hijack")): 1.0}

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
