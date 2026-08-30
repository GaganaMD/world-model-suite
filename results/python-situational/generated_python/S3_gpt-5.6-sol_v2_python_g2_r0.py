from posg import POSG

class AirportCurbPOSG(POSG):
    """Player 0 is the self-driving car, player 1 the man, and player 2 the woman.

    The state's sole coordinate records that the man is aboard. This is terminal
    because the described boarding has already occurred and no subsequent act is
    specified.
    """

    n_players = 3

    def initial_distribution(self):
        state = ("aboard",)
        observations = ("aboard", "aboard", "aboard")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("aboard",)

    def legal_actions(self, s, i):
        return ("noop",)

    def transition(self, s, a):
        return {(s, ("aboard", "aboard", "aboard")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
