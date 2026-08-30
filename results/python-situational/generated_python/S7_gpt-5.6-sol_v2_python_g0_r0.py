from posg import POSG

ARRIVAL = ("arrival_due", "unexamined", "barking", "absent", "held")
EXAMINATION = ("examination_due", "unexamined", "barking", "absent", "held")
DROP = ("drop_due", "locked", "barking", "absent", "held")
DROPPED = ("ended", "locked", "barking", "absent", "dropped")


class LockedGateDelivery(POSG):
    """Player 0 is the delivery drone; player 1 is the dog.

    State tuple coordinates are interaction phase, closure condition,
    dog activity, human response condition, and package condition.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (ARRIVAL, ("barking", "drone_present")): 1.0
        }

    def is_terminal(self, s):
        return s == DROPPED

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("invalid player index")
        if self.is_terminal(s):
            return ("noop",)
        if i == 1:
            return ("bark",)
        if s == ARRIVAL:
            return ("arrive",)
        if s == EXAMINATION:
            return ("find",)
        if s == DROP:
            return ("drop_off",)
        raise ValueError("unknown state")

    def transition(self, s, a):
        if self.is_terminal(s):
            if a != ("noop", "noop"):
                raise ValueError("illegal action profile")
            return {
                (DROPPED, ("none", "none")): 1.0
            }

        if s == ARRIVAL and a == ("arrive", "bark"):
            return {
                (EXAMINATION, ("barking", "drone_present")): 1.0
            }

        if s == EXAMINATION and a == ("find", "bark"):
            return {
                (DROP, ("locked", "none")): 1.0
            }

        if s == DROP and a == ("drop_off", "bark"):
            return {
                (DROPPED, ("package_dropped", "none")): 1.0
            }

        raise ValueError("illegal action profile")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
