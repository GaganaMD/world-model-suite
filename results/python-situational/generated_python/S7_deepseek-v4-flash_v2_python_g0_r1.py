from posg import POSG

class DeliveryDronePOSG(POSG):
    """POSG for a delivery drone arriving at a locked gate with a barking dog.

    Players:
        0: Drone
        1: Dog

    States:
        "at_gate": Drone is at the gate, gate locked, dog barking.
        "left": Drone has left (terminal).

    Actions:
        Drone: "wait" or "leave"
        Dog: "bark" (always)

    Observations:
        Drone: "gate_locked_dog_barking" (at gate), "none" (after leaving)
        Dog: "drone_present" (at gate), "drone_gone" (after leaving)
    """
    n_players = 2

    def initial_distribution(self):
        return {("at_gate", ("gate_locked_dog_barking", "drone_present")): 1.0}

    def is_terminal(self, s):
        return s == "left"

    def legal_actions(self, s, i):
        if s == "at_gate":
            if i == 0:  # drone
                return ("wait", "leave")
            elif i == 1:  # dog
                return ("bark",)
        # Terminal state: should not be called, but return a noop for safety
        return ("noop",)

    def transition(self, s, a):
        if s == "at_gate":
            drone_action = a[0]  # dog action is always "bark", ignored
            if drone_action == "wait":
                return {("at_gate", ("gate_locked_dog_barking", "drone_present")): 1.0}
            elif drone_action == "leave":
                return {("left", ("none", "drone_gone")): 1.0}
        # Should not reach here
        return {}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
