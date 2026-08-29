from posg import POSG

DRONE, DOG, RESIDENT = 0, 1, 2

OCCUPANCY = ("present", "absent")
ACCESS = ("unanswered", "answered", "unlocked")
DOG_STATE = ("barking", "quiet")
CLOSURE = ("pending", "released", "withdrawn")

HEAR_BARKING = 0.9


class LockedGateDelivery(POSG):
    """Delivery drone held at a locked gate, a barking dog inside, no answer yet.

    Player 0 -- the delivery drone: it can hold off, let the package go, or break off.
    Player 1 -- the dog in the yard: it can keep barking or settle.
    Player 2 -- the household: it may or may not be there to react; if it is, it can
                stay inside, come to the door, and open the gate.

    State is a 4-tuple (occupancy, access, dog, closure):
      occupancy -- 'present' / 'absent': whether anyone in the house can react at all
                   (hidden from the drone).
      access    -- 'unanswered' (no one at the door), 'answered' (someone at the door),
                   'unlocked' (the gate no longer bars the drone).
      dog       -- 'barking' / 'quiet'.
      closure   -- 'pending', 'released' (the package has been let go),
                   'withdrawn' (the drone has broken off).  The latter two are terminal.
    """

    n_players = 3

    # ---------- helpers ----------

    @staticmethod
    def _drone_obs(access, dog, closure):
        if closure == "released":
            return "released"
        if closure == "withdrawn":
            return "departed"
        return access + "_" + dog

    @staticmethod
    def _dog_obs(closure):
        return "drone_gone" if closure != "pending" else "drone_present"

    @staticmethod
    def _resident_obs_dist(occupancy, access, dog, closure):
        """Distribution over what the household perceives."""
        if occupancy == "absent":
            return ((("none"), 1.0),)
        if access in ("answered", "unlocked"):
            if closure == "released":
                return (("released", 1.0),)
            if closure == "withdrawn":
                return (("departed", 1.0),)
            return (("drone_present", 1.0),)
        if dog == "barking":
            return (("barking", HEAR_BARKING), ("quiet", 1.0 - HEAR_BARKING))
        return (("quiet", 1.0),)

    # ---------- interface ----------

    def initial_distribution(self):
        out = {}
        for occupancy, p_occ in (("present", 0.5), ("absent", 0.5)):
            s = (occupancy, "unanswered", "barking", "pending")
            o_drone = self._drone_obs("unanswered", "barking", "pending")
            o_dog = self._dog_obs("pending")
            for o_res, p_res in self._resident_obs_dist(
                occupancy, "unanswered", "barking", "pending"
            ):
                key = (s, (o_drone, o_dog, o_res))
                out[key] = out.get(key, 0.0) + p_occ * p_res
        return out

    def is_terminal(self, s):
        return s[3] != "pending"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        occupancy, access, dog, closure = s
        if i == DRONE:
            return ("wait", "release_package", "depart")
        if i == DOG:
            return ("bark", "settle")
        if occupancy == "absent":
            return ("noop",)
        if access == "unanswered":
            return ("stay_inside", "come_to_door")
        if access == "answered":
            return ("unlock_gate", "wait")
        return ("noop",)

    def transition(self, s, a):
        occupancy, access, dog, closure = s
        drone_a, dog_a, res_a = a

        new_dog = "barking" if dog_a == "bark" else "quiet"

        if drone_a == "release_package":
            new_closure = "released"
        elif drone_a == "depart":
            new_closure = "withdrawn"
        else:
            new_closure = "pending"

        if res_a == "come_to_door":
            access_branches = (("answered", 0.8), ("unanswered", 0.2))
        elif res_a == "unlock_gate":
            access_branches = (("unlocked", 1.0),)
        else:
            access_branches = ((access, 1.0),)

        out = {}
        for new_access, p_acc in access_branches:
            s2 = (occupancy, new_access, new_dog, new_closure)
            o_drone = self._drone_obs(new_access, new_dog, new_closure)
            o_dog = self._dog_obs(new_closure)
            for o_res, p_res in self._resident_obs_dist(
                occupancy, new_access, new_dog, new_closure
            ):
                key = (s2, (o_drone, o_dog, o_res))
                out[key] = out.get(key, 0.0) + p_acc * p_res
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
