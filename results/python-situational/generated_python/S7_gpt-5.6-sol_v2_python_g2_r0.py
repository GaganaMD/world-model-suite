from posg import POSG

class LockedGateDelivery(POSG):
    """Players: 0 is the delivery drone; 1 is the dog.

    State tuple fields are:
    (drone_condition, package_condition, gate_condition,
     dog_condition, door_response).

    The gate condition records both that it is locked and whether the drone
    has found that out.
    """

    n_players = 2

    _INITIAL = (
        "arrival_pending",
        "carried",
        "locked_unnoticed",
        "no_target",
        "not_observed",
    )
    _ARRIVED = (
        "arrived",
        "carried",
        "locked_unnoticed",
        "target_present",
        "no_response",
    )
    _FOUND = (
        "arrived",
        "carried",
        "locked_known",
        "target_present",
        "no_response",
    )
    _DROPPED = (
        "arrived",
        "dropped",
        "locked_known",
        "target_present",
        "no_response",
    )

    def initial_distribution(self):
        return {(self._INITIAL, ("none", "none")): 1.0}

    def is_terminal(self, s):
        return s == self._DROPPED

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("invalid player")

        if s == self._INITIAL:
            return ("arrive",) if i == 0 else ("noop",)
        if s == self._ARRIVED:
            return ("find",) if i == 0 else ("bark",)
        if s == self._FOUND:
            return ("drop_off",) if i == 0 else ("bark",)
        if s == self._DROPPED:
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        if len(a) != self.n_players:
            raise ValueError("invalid action profile")
        if any(a[i] not in self.legal_actions(s, i) for i in range(self.n_players)):
            raise ValueError("illegal action profile")

        if s == self._INITIAL:
            return {
                (self._ARRIVED, ("arrived", "drone_present")): 1.0
            }
        if s == self._ARRIVED:
            return {
                (
                    self._FOUND,
                    ("gate_locked_barking_no_answer", "drone_present"),
                ): 1.0
            }
        if s == self._FOUND:
            return {
                (self._DROPPED, ("barking", "package_dropped")): 1.0
            }
        if s == self._DROPPED:
            return {(self._DROPPED, ("none", "none")): 1.0}

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
