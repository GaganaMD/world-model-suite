from posg import POSG

class WarehouseForkliftPOSG(POSG):
    """Player 0 is the warehouse robot; player 1 is the child.

    The state tuple's coordinate records the current enabling condition:
    forklift_ready, forklift_operating, child_noticed, route_taken, or
    pallet_moved.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("forklift_ready",), ("none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("pallet_moved",)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)

        if i == 1:
            return ("stand",)

        actions = {
            ("forklift_ready",): ("operate_forklift",),
            ("forklift_operating",): ("notice_child",),
            ("child_noticed",): ("take_path",),
            ("route_taken",): ("move_pallet",),
        }
        return actions[s]

    def transition(self, s, a):
        if self.is_terminal(s):
            return {
                (s, ("child_seen_adult_unseen", "none")): 1.0
            }

        successors = {
            ("forklift_ready",): ("forklift_operating",),
            ("forklift_operating",): ("child_noticed",),
            ("child_noticed",): ("route_taken",),
            ("route_taken",): ("pallet_moved",),
        }
        s_next = successors[s]

        robot_observation = (
            "none"
            if s_next == ("forklift_operating",)
            else "child_seen_adult_unseen"
        )
        return {
            (s_next, (robot_observation, "none")): 1.0
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
