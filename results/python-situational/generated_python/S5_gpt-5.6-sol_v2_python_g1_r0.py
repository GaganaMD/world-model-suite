from posg import POSG

class WarehouseForkliftPOSG(POSG):
    """Player 0 is the warehouse robot; player 1 is the child.

    Each state is a tuple whose sole coordinate records the current condition:
    forklift_present, forklift_operating, child_noticed, path_taken, or
    pallet_moved.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("forklift_present",), ("forklift_present", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("pallet_moved",)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)

        robot_actions = {
            ("forklift_present",): ("operate",),
            ("forklift_operating",): ("notice",),
            ("child_noticed",): ("take_path",),
            ("path_taken",): ("move_pallet",),
        }

        if i == 0:
            return robot_actions[s]
        if i == 1:
            return ("stand",)
        raise IndexError("player index out of range")

    def transition(self, s, a):
        expected = tuple(self.legal_actions(s, i)[0] for i in range(self.n_players))
        if a != expected:
            raise ValueError("illegal action profile")

        if s == ("forklift_present",):
            return {
                (("forklift_operating",), ("none", "none")): 1.0
            }
        if s == ("forklift_operating",):
            return {
                (("child_noticed",), ("child_alone", "none")): 1.0
            }
        if s == ("child_noticed",):
            return {
                (("path_taken",), ("child_alone", "none")): 1.0
            }
        if s == ("path_taken",):
            return {
                (("pallet_moved",), ("child_alone", "none")): 1.0
            }
        if s == ("pallet_moved",):
            return {
                (("pallet_moved",), ("none", "none")): 1.0
            }
        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
