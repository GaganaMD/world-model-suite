from posg import POSG

class PackageHandoffPOSG(POSG):
    """Players: index 0 is the household robot; index 1 is the delivery boy.

    The sole state coordinate is the handoff condition:
    `package_to_hand` permits moving or handing the package, while
    `package_handed` is terminal.
    """

    n_players = 2

    def initial_distribution(self):
        state = ("package_to_hand",)
        observations = ("order_known", "traffic_blocked")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("package_handed",)

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("player index out of range")
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("noop",)
        return ("move", "hand")

    def transition(self, s, a):
        if len(a) != self.n_players:
            raise ValueError("action profile has wrong length")
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}
        if a[0] != "noop":
            raise ValueError("illegal robot action")
        if a[1] == "move":
            return {(("package_to_hand",), ("rattle", "rattle")): 1.0}
        if a[1] == "hand":
            return {(("package_handed",), ("handed", "handed")): 1.0}
        raise ValueError("illegal delivery boy action")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
