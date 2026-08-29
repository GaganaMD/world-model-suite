from posg import POSG

from collections.abc import Mapping, Sequence


class AirportCurbPickup(POSG):
    """Two-player simultaneous-move POSG at an airport pickup curb.

    Player 0 is the self-driving car (the driver).
    Player 1 is the passenger, a man in a suit who has just boarded.

    State is a tuple (car_status, passenger_status, woman_status):
      car_status     in {"waiting", "departed"}
      passenger_status in {"aboard", "exited"}
      woman_status   in {"standing", "assisted", "unassisted"}

    Terminal when car_status == "departed".
    """

    n_players = 2

    _CAR_WAITING = "waiting"
    _CAR_DEPARTED = "departed"
    _PASSENGER_ABOARD = "aboard"
    _PASSENGER_EXITED = "exited"
    _WOMAN_STANDING = "standing"
    _WOMAN_ASSISTED = "assisted"
    _WOMAN_UNASSISTED = "unassisted"

    # ---- helpers ---------------------------------------------------------

    def _obs(self, s):
        car_status, passenger_status, woman_status = s
        if car_status == self._CAR_DEPARTED:
            return ("departed", "departed")
        if passenger_status == self._PASSENGER_ABOARD:
            return ("aboard", "aboard")
        return ("exited", "exited")

    # ---- POSG interface --------------------------------------------------

    def initial_distribution(self):
        s0 = (self._CAR_WAITING, self._PASSENGER_ABOARD, self._WOMAN_STANDING)
        return {(s0, self._obs(s0)): 1.0}

    def is_terminal(self, s):
        return s[0] == self._CAR_DEPARTED

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("proceed", "wait")
        return ("stay", "exit")

    def transition(self, s, a):
        car_status, passenger_status, woman_status = s
        car_act, pas_act = a

        if car_status == self._CAR_DEPARTED:
            ns = (self._CAR_DEPARTED, passenger_status, woman_status)
            return {(ns, self._obs(ns)): 1.0}

        # car decides whether to depart
        if car_act == "proceed":
            ns = (self._CAR_DEPARTED, passenger_status, woman_status)
            return {(ns, self._obs(ns)): 1.0}

        # car waits; passenger may stay aboard or exit
        if pas_act == "stay":
            ns = (self._CAR_WAITING, self._PASSENGER_ABOARD, woman_status)
            return {(ns, self._obs(ns)): 1.0}

        # passenger exits; the car then chooses whether to assist the woman
        if car_act == "assist":
            ns = (self._CAR_WAITING, self._PASSENGER_EXITED, self._WOMAN_ASSISTED)
            return {(ns, self._obs(ns)): 1.0}
        ns = (self._CAR_WAITING, self._PASSENGER_EXITED, self._WOMAN_UNASSISTED)
        return {(ns, self._obs(ns)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
