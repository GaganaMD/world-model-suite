from posg import POSG

class HomeRecoveryPOSG(POSG):
    """Interaction among the care robot, man, daughter, and son, in profile order.

    Each state is a one-coordinate tuple whose coordinate identifies the current
    interaction condition: context being established, views being expressed,
    the man's choice being open, rest being due, transport being due, resting,
    or taken out.
    """

    n_players = 4

    def initial_distribution(self):
        state = ("context_open",)
        observations = (
            "tired_appearance",
            "recovering",
            "tired_appearance",
            "none",
        )
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s in (("resting",), ("taken_out",))

    def legal_actions(self, s, i):
        if i < 0 or i >= self.n_players:
            raise IndexError("player index out of range")

        phase = s[0]

        if phase == "context_open":
            return (
                ("look_after",),
                ("recover",),
                ("live_with",),
                ("visit",),
            )[i]

        if phase == "views_open":
            return (
                ("look_after",),
                ("say_wants_go",),
                ("say_stay_and_rest",),
                ("offer_take_out",),
            )[i]

        if phase == "choice_open":
            return (
                ("look_after",),
                ("stay", "go"),
                ("noop",),
                ("noop",),
            )[i]

        if phase == "rest_due":
            return (
                ("look_after",),
                ("rest",),
                ("noop",),
                ("noop",),
            )[i]

        if phase == "take_out_due":
            return (
                ("noop",),
                ("noop",),
                ("noop",),
                ("take_out",),
            )[i]

        if self.is_terminal(s):
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        if len(a) != self.n_players:
            raise ValueError("action profile has wrong length")

        legal_profile = tuple(self.legal_actions(s, i) for i in range(self.n_players))
        if any(a[i] not in legal_profile[i] for i in range(self.n_players)):
            raise ValueError("illegal action profile")

        phase = s[0]

        if phase == "context_open":
            s_next = ("views_open",)
            observations = (
                "tired_appearance",
                "recovering",
                "tired_appearance",
                "tired_appearance",
            )
            return {(s_next, observations): 1.0}

        if phase == "views_open":
            s_next = ("choice_open",)
            observations = (
                "views_expressed",
                "views_expressed",
                "views_expressed",
                "views_expressed",
            )
            return {(s_next, observations): 1.0}

        if phase == "choice_open":
            if a[1] == "stay":
                s_next = ("rest_due",)
                observations = ("staying", "staying", "staying", "staying")
            else:
                s_next = ("take_out_due",)
                observations = ("going", "going", "going", "going")
            return {(s_next, observations): 1.0}

        if phase == "rest_due":
            s_next = ("resting",)
            observations = ("resting", "resting", "resting", "resting")
            return {(s_next, observations): 1.0}

        if phase == "take_out_due":
            s_next = ("taken_out",)
            observations = ("taken_out", "taken_out", "taken_out", "taken_out")
            return {(s_next, observations): 1.0}

        if self.is_terminal(s):
            observations = ("none", "none", "none", "none")
            return {(s, observations): 1.0}

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
