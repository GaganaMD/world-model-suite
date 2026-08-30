from posg import POSG

class FactoryLockoutPOSG(POSG):
    """Player 0 is the factory robot; player 1 is the human coworker.

    The state tuple has one coordinate describing the current condition:
    "lockout_pending", "reach_pending", or "ended".
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("lockout_pending",), ("none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("ended",)

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("player index out of range")

        condition = s[0]

        if condition == "lockout_pending":
            return ("observe",) if i == 0 else ("skip",)
        if condition == "reach_pending":
            return ("noop",) if i == 0 else ("reach",)
        if condition == "ended":
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        condition = s[0]

        if condition == "lockout_pending":
            if a != ("observe", "skip"):
                raise ValueError("illegal action profile")
            return {
                (("reach_pending",), ("skip_seen", "none")): 1.0
            }

        if condition == "reach_pending":
            if a != ("noop", "reach"):
                raise ValueError("illegal action profile")
            return {
                (("ended",), ("none", "none")): 1.0
            }

        if condition == "ended":
            if a != ("noop", "noop"):
                raise ValueError("illegal action profile")
            return {
                (("ended",), ("none", "none")): 1.0
            }

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
