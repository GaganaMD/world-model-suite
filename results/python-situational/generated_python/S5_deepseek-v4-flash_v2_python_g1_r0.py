from posg import POSG

class WarehouseChildPOSG(POSG[str, str, str]):
    """POSG with two players: 0 = warehouse robot, 1 = child.

    States are single strings: 'near' (child near path), 'away' (child out of path),
    'done' (pallet moved safely), 'crash' (collision).  The robot observes child
    location or terminal outcome; the child always observes 'none'.
    """

    n_players = 2

    def initial_distribution(self):
        # robot sees child near; child sees nothing
        return {("near", ("child_near", "none")): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s in ("done", "crash")

    def legal_actions(self, s: str, i: int):
        if s in ("near", "away"):
            if i == 0:               # robot
                return ("proceed", "stop")
            else:                    # child
                return ("stay", "leave")
        else:                         # terminal states
            return ("none",)

    def transition(self, s: str, a):
        robot_act, child_act = a

        # terminal states are absorbing
        if s in ("done", "crash"):
            return {(s, ("none", "none")): 1.0}

        if s == "near":
            if robot_act == "proceed" and child_act == "stay":
                return {("crash", ("crash", "none")): 1.0}
            elif robot_act == "proceed" and child_act == "leave":
                return {("done", ("pallet_moved", "none")): 1.0}
            elif robot_act == "stop" and child_act == "stay":
                return {("near", ("child_near", "none")): 1.0}
            else:  # robot stop, child leave
                return {("away", ("child_away", "none")): 1.0}
        else:  # s == "away"
            if robot_act == "proceed":
                return {("done", ("pallet_moved", "none")): 1.0}
            else:  # robot stop
                return {("away", ("child_away", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
