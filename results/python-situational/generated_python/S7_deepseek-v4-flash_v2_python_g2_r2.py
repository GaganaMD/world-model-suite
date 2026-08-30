from posg import POSG

class DeliveryDronePOSG(POSG):
    """POSG for a delivery drone at a locked gate with a barking dog.

    Players:
        0: Drone
        1: Human (resident)

    States are strings:
        "locked"   – gate locked, drone present, dog barking, human inside
        "unlocked" – gate unlocked, drone present, dog barking, human inside
        "left"     – terminal: drone left
        "delivered"– terminal: package delivered
    """
    n_players = 2

    def initial_distribution(self):
        return {("locked", ("gate_locked_dog_barking", "none")): 1.0}

    def is_terminal(self, s):
        return s in ("left", "delivered")

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:  # drone
            if s == "locked":
                return ("wait", "leave")
            else:  # unlocked
                return ("wait", "leave", "deliver")
        else:  # human
            return ("stay_inside", "come_to_gate")

    def transition(self, s, a):
        drone_act, human_act = a
        if s == "locked":
            if drone_act == "leave":
                return {("left", ("left", "drone_left")): 1.0}
            else:  # wait
                if human_act == "stay_inside":
                    return {("locked", ("none", "none")): 1.0}
                else:  # come_to_gate
                    return {("unlocked", ("gate_opened", "none")): 1.0}
        elif s == "unlocked":
            if drone_act == "leave":
                return {("left", ("left", "drone_left")): 1.0}
            elif drone_act == "deliver":
                return {("delivered", ("delivered", "package_delivered")): 1.0}
            else:  # wait
                return {("unlocked", ("none", "none")): 1.0}
        else:  # terminal – should not be called
            return {(s, ("none", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
