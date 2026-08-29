from posg import POSG

class DeliveryHandoffPOSG(POSG):
    """Player 0 is the household robot, player 1 is the owner, and player 2
    is the delivery boy. The sole state coordinate records whether ordering
    or handing is currently available, or whether the interaction is closed.
    """

    n_players = 3

    def initial_distribution(self):
        return {
            (("order_open",), ("none", "none", "traffic_blocked")): 1.0
        }

    def is_terminal(self, s):
        return s == ("closed",)

    def legal_actions(self, s, i):
        if s == ("order_open",):
            return ("order",) if i == 1 else ("noop",)
        if s == ("handoff_open",):
            return ("hand",) if i == 2 else ("noop",)
        return ("noop",)

    def transition(self, s, a):
        if s == ("order_open",):
            return {
                (("handoff_open",), ("vase_ordered", "vase_ordered", "traffic_blocked")): 1.0
            }
        if s == ("handoff_open",):
            return {
                (("closed",), ("rattle", "none", "traffic_blocked")): 1.0
            }
        return {
            (("closed",), ("none", "none", "none")): 1.0
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
