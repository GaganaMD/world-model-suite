from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple


class DroneDeliveryGate(POSG):
    """
    Player 0: delivery drone
    Player 1: resident (the person who would open the gate)

    State tuple: (gate_open, resident_present, package_delivered)
      gate_open: bool - whether the gate is currently open
      resident_present: bool - whether the resident is present at the gate
      package_delivered: bool - whether the package has been delivered

    Terminal when package_delivered is True.
    """
    n_players = 2

    # --- helpers -----------------------------------------------------------

    def _obs(self, s):
        gate_open, resident_present, delivered = s
        if delivered:
            return ("delivered", "delivered")
        if resident_present:
            return ("resident_at_gate", "at_gate")
        if gate_open:
            return ("gate_open", "gate_open")
        return ("gate_locked", "no_one")

    def _terminal_obs(self):
        return ("delivered", "delivered")

    # --- POSG interface ----------------------------------------------------

    def initial_distribution(self) -> Mapping[Tuple[Tuple, Tuple], float]:
        s0 = (False, False, False)
        o0 = self._obs(s0)
        return {(s0, o0): 1.0}

    def is_terminal(self, s) -> bool:
        return s[2]

    def legal_actions(self, s, i) -> Sequence[str]:
        gate_open, resident_present, delivered = s
        if delivered:
            return ("noop",)
        if i == 0:
            if resident_present:
                return ("deliver",)
            if gate_open:
                return ("enter", "leave")
            return ("wait", "leave")
        else:  # i == 1
            if resident_present:
                return ("open_gate", "noop")
            return ("come_out", "stay_in")

    def transition(self, s, a) -> Mapping[Tuple[Tuple, Tuple], float]:
        gate_open, resident_present, delivered = s
        if delivered:
            return {((True, True, True), self._terminal_obs()): 1.0}

        drone_act = a[0]
        res_act = a[1]

        # Resident comes out / opens gate
        if res_act == "come_out":
            new_resident = True
            new_gate = gate_open
        elif res_act == "open_gate":
            new_resident = True
            new_gate = True
        else:  # stay_in / noop
            new_resident = resident_present
            new_gate = gate_open

        # Drone acts
        if drone_act == "deliver":
            new_delivered = True
        elif drone_act == "enter":
            new_delivered = False
        else:  # wait / leave
            new_delivered = False

        ns = (new_gate, new_resident, new_delivered)
        o = self._obs(ns)
        return {(ns, o): 1.0}

    def rewards(self, s, a, s_next) -> Tuple[float, ...]:
        return (0.0, 0.0)
