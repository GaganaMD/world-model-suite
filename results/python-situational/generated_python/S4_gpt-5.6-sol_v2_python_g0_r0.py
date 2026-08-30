from posg import POSG

class ClassroomReactionPOSG(POSG):
    """Player index 0 is the robot teacher, index 1 is the giggling students,
    and index 2 is the protesting students. The state's sole coordinate records
    whether the description awaits reading, reactions are occurring, or the
    interaction has closed.
    """

    n_players = 3

    def initial_distribution(self):
        return {
            (("description_awaits_reading",), ("none", "none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("interaction_closed",)

    def legal_actions(self, s, i):
        if s == ("description_awaits_reading",):
            return ("read_aloud",) if i == 0 else ("noop",)
        if s == ("reactions_occurring",):
            if i == 0:
                return ("noop",)
            if i == 1:
                return ("giggle",)
            return ("protest",)
        return ()

    def transition(self, s, a):
        if s == ("description_awaits_reading",):
            if a != ("read_aloud", "noop", "noop"):
                raise ValueError("illegal action profile")
            return {
                (
                    ("reactions_occurring",),
                    ("description_heard", "description_heard", "description_heard"),
                ): 1.0
            }

        if s == ("reactions_occurring",):
            if a != ("noop", "giggle", "protest"):
                raise ValueError("illegal action profile")
            return {
                (
                    ("interaction_closed",),
                    ("reactions_heard", "reactions_heard", "reactions_heard"),
                ): 1.0
            }

        raise ValueError("terminal state has no transition")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
