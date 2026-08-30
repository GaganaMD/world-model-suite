from posg import POSG

class ShuttlePOSG(POSG):
    """One-player POSG: a self-driving shuttle with one seat left must choose
    which waiting person to board.  The state is a 4-tuple of booleans
    indicating whether each of the four people (elderly, parent, commuter,
    teenager) is still waiting.  The terminal state is the string 'terminal'.
    """
    n_players = 1

    def initial_distribution(self):
        s0 = (True, True, True, True)          # all waiting
        o0 = (s0,)                             # shuttle sees the state
        return {(s0, o0): 1.0}

    def is_terminal(self, s):
        return s == "terminal"

    def legal_actions(self, s, i):
        if s == "terminal":
            return ("noop",)
        # s is a tuple of booleans
        acts = []
        if s[0]:
            acts.append("board_elderly")
        if s[1]:
            acts.append("board_parent")
        if s[2]:
            acts.append("board_commuter")
        if s[3]:
            acts.append("board_teenager")
        return tuple(acts)

    def transition(self, s, a):
        if s == "terminal":
            return {("terminal", ("none",)): 1.0}
        # from the initial state, any boarding action ends the game
        return {("terminal", ("none",)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0,)
