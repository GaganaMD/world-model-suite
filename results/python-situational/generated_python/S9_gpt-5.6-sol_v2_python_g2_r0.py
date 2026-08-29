from posg import POSG

class HomeRecoveryPOSG(POSG):
    """POSG for resolving whether an elderly man rests or attends a gathering.

    Player 0 is the care robot.
    Player 1 is the elderly man.
    Player 2 is his adult daughter.
    Player 3 is his visiting son.

    The state tuple has one coordinate: the current interaction condition.
    """

    n_players = 4

    def initial_distribution(self):
        state = ("statements",)
        observations = ("tired", "tired", "tired", "tired")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s[0] in ("resting", "gathering")

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "statements":
            actions = (
                ("look_after",),
                ("say_wants_go",),
                ("say_stay_and_rest",),
                ("offer_take_out",),
            )
            return actions[i]

        if condition == "choice":
            actions = (
                ("look_after",),
                ("stay_home", "go"),
                ("noop",),
                ("noop",),
            )
            return actions[i]

        if condition == "staying":
            actions = (
                ("look_after",),
                ("rest",),
                ("noop",),
                ("noop",),
            )
            return actions[i]

        return ("noop",)

    def transition(self, s, a):
        condition = s[0]

        if condition == "statements":
            next_state = ("choice",)
            observations = (
                "views_heard",
                "views_heard",
                "views_heard",
                "views_heard",
            )
            return {(next_state, observations): 1.0}

        if condition == "choice":
            if a[1] == "stay_home":
                next_state = ("staying",)
                observations = (
                    "staying_home",
                    "staying_home",
                    "staying_home",
                    "staying_home",
                )
            else:
                next_state = ("gathering",)
                observations = (
                    "going_to_gathering",
                    "going_to_gathering",
                    "going_to_gathering",
                    "going_to_gathering",
                )
            return {(next_state, observations): 1.0}

        if condition == "staying":
            next_state = ("resting",)
            observations = ("resting", "resting", "resting", "resting")
            return {(next_state, observations): 1.0}

        observations = ("none", "none", "none", "none")
        return {(s, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
