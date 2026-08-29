from posg import POSG

class VaseDeliveryPOSG(POSG):
    """Players: 0 is the owner, 1 is the household robot, and 2 is the delivery boy.

    Each state is a one-coordinate tuple whose coordinate records the current
    interaction condition: the owner can order, the delivery boy can hand over
    the package, the robot can move the package, or the package has been moved.
    """

    n_players = 3

    def initial_distribution(self):
        s = ("owner_can_order",)
        o = ("order_available", "none", "none")
        return {(s, o): 1.0}

    def is_terminal(self, s):
        return s == ("package_moved",)

    def legal_actions(self, s, i):
        if i not in (0, 1, 2):
            raise IndexError("player index out of range")

        condition = s[0]

        if condition == "owner_can_order":
            return ("order",) if i == 0 else ("noop",)
        if condition == "boy_can_hand":
            return ("hand",) if i == 2 else ("noop",)
        if condition == "robot_can_move":
            return ("move",) if i == 1 else ("noop",)
        if condition == "package_moved":
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        if len(a) != self.n_players:
            raise ValueError("action profile has wrong length")

        condition = s[0]

        if condition == "owner_can_order":
            if a != ("order", "noop", "noop"):
                raise ValueError("illegal action profile")
            s_next = ("boy_can_hand",)
            o = ("order_made", "order_known", "traffic_blocked")
            return {(s_next, o): 1.0}

        if condition == "boy_can_hand":
            if a != ("noop", "noop", "hand"):
                raise ValueError("illegal action profile")
            s_next = ("robot_can_move",)
            o = ("none", "package_received", "package_handed")
            return {(s_next, o): 1.0}

        if condition == "robot_can_move":
            if a != ("noop", "move", "noop"):
                raise ValueError("illegal action profile")
            s_next = ("package_moved",)
            o = ("none", "rattle_heard", "none")
            return {(s_next, o): 1.0}

        if condition == "package_moved":
            if a != ("noop", "noop", "noop"):
                raise ValueError("illegal action profile")
            return {(s, ("none", "none", "none")): 1.0}

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
