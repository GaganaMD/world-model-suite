from posg import POSG

class LockedGateDelivery(POSG):
    """Delivery drone at a house with a locked gate, a barking dog and an unanswered door.

    Players:
      0 - delivery drone (outside the locked gate, holding the package)
      1 - dog inside the yard
      2 - resident inside the house

    State is a 3-tuple (dog_condition, door_condition, package_condition):
      s[0] dog_condition     : 'barking' | 'quiet'
      s[1] door_condition    : 'unanswered' | 'answered'
      s[2] package_condition : 'pending' | 'left'   ('left' is terminal)

    The gate stays locked throughout, so the drone can never simply walk the
    package in; a drop_off attempt may or may not put the package down.

    Actions:
      drone    : 'drop_off' | 'wait'
      dog      : 'bark' | 'wait'
      resident : 'answer' | 'wait'  (while unanswered), 'noop' (once answered)

    Observations:
      drone    : 'package_left' | 'person_present' | 'barking' | 'quiet'
      dog      : 'person_present' | 'none'
      resident : 'package_left' | 'drone_present' | 'barking' | 'none'
                 (inside the house the resident only hears the dog, so a
                  drop_off made at the locked gate is indistinguishable from
                  none being made)
    """

    n_players = 3

    _DROP_ODDS = {
        ("answered", "quiet"): (0.9, 0.1),
        ("answered", "barking"): (0.7, 0.3),
        ("unanswered", "quiet"): (0.4, 0.6),
        ("unanswered", "barking"): (0.2, 0.8),
    }

    @staticmethod
    def _obs(s):
        dog_c, door_c, pkg_c = s
        if pkg_c == "left":
            drone_o = "package_left"
        elif door_c == "answered":
            drone_o = "person_present"
        elif dog_c == "barking":
            drone_o = "barking"
        else:
            drone_o = "quiet"

        dog_o = "person_present" if door_c == "answered" else "none"

        if door_c == "answered":
            res_o = "package_left" if pkg_c == "left" else "drone_present"
        else:
            res_o = "barking" if dog_c == "barking" else "none"

        return (drone_o, dog_o, res_o)

    def initial_distribution(self):
        s0 = ("barking", "unanswered", "pending")
        return {(s0, self._obs(s0)): 1.0}

    def is_terminal(self, s):
        return s[2] == "left"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("drop_off", "wait")
        if i == 1:
            return ("bark", "wait")
        if s[1] == "unanswered":
            return ("answer", "wait")
        return ("noop",)

    def transition(self, s, a):
        a_drone, a_dog, a_res = a

        dog_c = "barking" if a_dog == "bark" else "quiet"
        door_c = "answered" if (s[1] == "answered" or a_res == "answer") else "unanswered"

        out = {}
        if a_drone == "drop_off":
            p_left, p_pending = self._DROP_ODDS[(door_c, dog_c)]
            s_left = (dog_c, door_c, "left")
            s_pending = (dog_c, door_c, "pending")
            out[(s_left, self._obs(s_left))] = p_left
            out[(s_pending, self._obs(s_pending))] = p_pending
        else:
            s_pending = (dog_c, door_c, "pending")
            out[(s_pending, self._obs(s_pending))] = 1.0
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
