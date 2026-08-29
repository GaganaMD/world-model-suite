from posg import POSG

class HomeCarePOSG(POSG):
    """Care and outing decision game.

    Player 0 is the care robot.
    Player 1 is the recovering man.
    Player 2 is his daughter.
    Player 3 is his son.

    The sole state coordinate is the current condition of the interaction:
    views are being expressed, a choice is open, transport is pending, or
    the interaction is resolved.
    """

    n_players = 4

    def initial_distribution(self):
        state = ("expressing_views",)
        observations = ("tired", "none", "tired", "tired")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("resolved",)

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "expressing_views":
            return (
                ("look_after",),
                ("say_wants_go",),
                ("say_stay_rest",),
                ("offer_take_out",),
            )[i]

        if condition == "choice_open":
            if i == 0:
                return ("look_after",)
            if i == 1:
                return ("stay", "rest", "go")
            return ("noop",)

        if condition == "transport_pending":
            if i == 0:
                return ("look_after",)
            if i == 3:
                return ("take_out",)
            return ("noop",)

        return ("noop",)

    def transition(self, s, a):
        condition = s[0]

        if condition == "expressing_views":
            expected = (
                "look_after",
                "say_wants_go",
                "say_stay_rest",
                "offer_take_out",
            )
            if a != expected:
                raise ValueError("Illegal action profile")
            return {
                (("choice_open",), ("views_heard",) * self.n_players): 1.0
            }

        if condition == "choice_open":
            if a[1] == "stay":
                observations = ("staying",) * self.n_players
                return {(("resolved",), observations): 1.0}
            if a[1] == "rest":
                observations = ("resting",) * self.n_players
                return {(("resolved",), observations): 1.0}
            if a[1] == "go":
                observations = ("going",) * self.n_players
                return {(("transport_pending",), observations): 1.0}
            raise ValueError("Illegal action profile")

        if condition == "transport_pending":
            expected = ("look_after", "noop", "noop", "take_out")
            if a != expected:
                raise ValueError("Illegal action profile")
            return {
                (("resolved",), ("taken_out",) * self.n_players): 1.0
            }

        if condition == "resolved":
            if a != ("noop",) * self.n_players:
                raise ValueError("Illegal action profile")
            return {
                (("resolved",), ("none",) * self.n_players): 1.0
            }

        raise ValueError("Unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
