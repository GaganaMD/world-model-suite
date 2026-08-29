from posg import POSG

class ClassroomReactionPOSG(POSG):
    """Player 0 is the robot teacher, player 1 is the giggling student group,
    and player 2 is the protesting student group.

    The state is a one-coordinate tuple whose coordinate records whether the
    description is available to be read, has been heard, or reactions have
    been expressed.
    """

    n_players = 3

    def initial_distribution(self):
        state = ("description_available",)
        observations = ("description_present", "none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("reactions_expressed",)

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "description_available":
            return ("read_aloud",) if i == 0 else ("noop",)

        if condition == "description_heard":
            if i == 0:
                return ("noop",)
            if i == 1:
                return ("giggle",)
            return ("protest",)

        return ("noop",)

    def transition(self, s, a):
        condition = s[0]

        if condition == "description_available":
            next_state = ("description_heard",)
            observations = ("none", "description_heard", "description_heard")
            return {(next_state, observations): 1.0}

        if condition == "description_heard":
            next_state = ("reactions_expressed",)
            observations = (
                "reactions_heard",
                "reactions_heard",
                "reactions_heard",
            )
            return {(next_state, observations): 1.0}

        return {(s, ("none", "none", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
