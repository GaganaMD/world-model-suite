from posg import POSG

from collections.abc import Mapping, Sequence


class DroneDeliveryGate(POSG):
    """
    Player 0: delivery drone
    Player 1: resident

    State tuple: (gate_open, resident_present, package_delivered)
      gate_open: bool - whether the gate is open
      resident_present: bool - whether the resident is present at the door
      package_delivered: bool - whether the package has been delivered

    Terminal when package_delivered is True.
    """

    n_players = 2

    def initial_distribution(self) -> Mapping[tuple, float]:
        # Gate locked, no one at the door, package not yet delivered
        s0 = (False, False, False)
        o0 = ("locked", "absent")
        return {(s0, o0): 1.0}

    def is_terminal(self, s) -> bool:
        return s[2]  # package_delivered

    def legal_actions(self, s, i) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            # Drone: wait, or deliver (only possible if gate open and resident present)
            if s[0] and s[1]:
                return ("wait", "deliver")
            else:
                return ("wait",)
        else:
            # Resident: open gate, or stay absent
            return ("open_gate", "stay_absent")

    def transition(self, s, a) -> Mapping[tuple, float]:
        if self.is_terminal(s):
            return {(s, ("delivered", "delivered")): 1.0}

        drone_act = a[0]
        resident_act = a[1]

        gate_open = s[0]
        resident_present = s[1]
        delivered = s[2]

        # Update gate and resident presence based on resident's action
        if resident_act == "open_gate":
            new_gate_open = True
            new_resident_present = True
        else:  # stay_absent
            new_gate_open = gate_open
            new_resident_present = resident_present

        # Update delivery based on drone's action
        if drone_act == "deliver" and new_gate_open and new_resident_present:
            new_delivered = True
        else:
            new_delivered = delivered

        s_next = (new_gate_open, new_resident_present, new_delivered)

        # Observations
        if new_delivered:
            o_drone = "delivered"
            o_resident = "delivered"
        elif new_gate_open and new_resident_present:
            o_drone = "open"
            o_resident = "present"
        elif new_gate_open:
            o_drone = "open"
            o_resident = "absent"
        else:
            o_drone = "locked"
            o_resident = "absent"

        o_next = (o_drone, o_resident)
        return {((s_next, o_next)): 1.0}

    def rewards(self, s, a, s_next) -> tuple:
        return (0.0, 0.0)
