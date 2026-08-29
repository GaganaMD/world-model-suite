from posg import POSG

class BoardingSituationPOSG(POSG):
    """Player 0 is the self-driving car, player 1 the man, and player 2 the woman.

    The state tuple's sole coordinate records that the man's boarding has
    occurred, ending the depicted pickup interaction.
    """

    n_players = 3

    def initial_distribution(self):
        state = ("boarding_occurred",)
        observations = (
            "boarding_observed",
            "boarding_observed",
            "boarding_observed",
        )
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("boarding_occurred",)

    def legal_actions(self, s, i):
        return ("noop",)

    def transition(self, s, a):
        observations = (
            "boarding_observed",
            "boarding_observed",
            "boarding_observed",
        )
        return {(s, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
