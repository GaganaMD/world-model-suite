from posg import POSG

class AirportPickupPOSG(POSG):
    """Player 0 is the self-driving car, player 1 the man, and player 2 the woman.

    The sole state coordinate is the pickup condition: awaiting_boarding or boarded.
    """

    n_players = 3

    def initial_distribution(self):
        state = ("awaiting_boarding",)
        observations = ("none", "none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("boarded",)

    def legal_actions(self, s, i):
        if i not in range(self.n_players):
            raise IndexError("invalid player index")
        if self.is_terminal(s):
            return ("noop",)
        if s != ("awaiting_boarding",):
            raise ValueError("unknown state")
        return (("wait",), ("board",), ("stand",))[i]

    def transition(self, s, a):
        if self.is_terminal(s):
            if a != ("noop", "noop", "noop"):
                raise ValueError("illegal action profile")
            return {(s, ("none", "none", "none")): 1.0}

        if s != ("awaiting_boarding",):
            raise ValueError("unknown state")
        if a != ("wait", "board", "stand"):
            raise ValueError("illegal action profile")

        next_state = ("boarded",)
        observations = ("boarded", "boarded", "boarded")
        return {(next_state, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
