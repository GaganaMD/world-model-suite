from posg import POSG

class WarehouseForkliftPOSG(POSG):
    """Player index 0 is the warehouse robot; player index 1 is the child.

    The state's sole coordinate is the current interaction condition:
    forklift_in_use, child_noticeable, child_noticed, route_taken, or
    pallet_moved.
    """

    n_players = 2

    def initial_distribution(self):
        state = ("forklift_in_use",)
        observations = ("none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("pallet_moved",)

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("player index out of range")

        if self.is_terminal(s):
            return ("noop",)

        if i == 1:
            return ("stand",)

        actions = {
            ("forklift_in_use",): ("operate_forklift",),
            ("child_noticeable",): ("notice",),
            ("child_noticed",): ("take_path",),
            ("route_taken",): ("move_pallet",),
        }
        return actions[s]

    def transition(self, s, a):
        if len(a) != self.n_players:
            raise ValueError("invalid action profile")

        if self.is_terminal(s):
            if a != ("noop", "noop"):
                raise ValueError("illegal action profile")
            return {(s, ("none", "none")): 1.0}

        expected = (
            self.legal_actions(s, 0)[0],
            self.legal_actions(s, 1)[0],
        )
        if a != expected:
            raise ValueError("illegal action profile")

        outcomes = {
            ("forklift_in_use",): (
                ("child_noticeable",),
                ("none", "none"),
            ),
            ("child_noticeable",): (
                ("child_noticed",),
                ("child_present", "none"),
            ),
            ("child_noticed",): (
                ("route_taken",),
                ("none", "none"),
            ),
            ("route_taken",): (
                ("pallet_moved",),
                ("none", "none"),
            ),
        }
        s_next, observations = outcomes[s]
        return {(s_next, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
