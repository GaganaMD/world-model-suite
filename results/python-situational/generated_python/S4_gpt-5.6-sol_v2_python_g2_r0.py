from posg import POSG

class ClassroomReactionPOSG(POSG):
    """Player index 0 is the robot teacher, index 1 is the giggling students,
    and index 2 is the protesting students.

    The state is a tuple whose sole coordinate records whether the passage is
    available to read, the description has been heard, or the reactions have
    occurred.
    """

    n_players = 3

    def initial_distribution(self):
        return {
            (("passage_available",), ("passage_seen", "none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("reactions_occurred",)

    def legal_actions(self, s, i):
        if s == ("passage_available",):
            return ("read_aloud",) if i == 0 else ("noop",)
        if s == ("description_heard",):
            if i == 0:
                return ("noop",)
            if i == 1:
                return ("giggle",)
            return ("protest",)
        return ("noop",)

    def transition(self, s, a):
        if s == ("passage_available",):
            if a != ("read_aloud", "noop", "noop"):
                raise ValueError("illegal action profile")
            return {
                (("description_heard",),
                 ("description_heard", "description_heard", "description_heard")): 1.0
            }

        if s == ("description_heard",):
            if a != ("noop", "giggle", "protest"):
                raise ValueError("illegal action profile")
            return {
                (("reactions_occurred",),
                 ("reactions_heard", "reactions_heard", "reactions_heard")): 1.0
            }

        if s == ("reactions_occurred",):
            if a != ("noop", "noop", "noop"):
                raise ValueError("illegal action profile")
            return {
                (("reactions_occurred",), ("none", "none", "none")): 1.0
            }

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
