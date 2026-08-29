from posg import POSG

from collections.abc import Mapping, Sequence


class POSG(ABC, Generic[S, A, O]):
    """Two-player POSG: a self-driving car and a passenger.

    Player 0 = the self-driving car.
    Player 1 = the passenger (the man in a suit who has just boarded).

    State tuple (phase, passenger_status, woman_status):
      phase            : "waiting" | "driving"
      passenger_status : "boarded" | "seated" | "departed"
      woman_status     : "standing" | "assisted" | "unassisted"

    Terminal when the passenger has departed (the ride is complete).
    """

    n_players = 2

    # --- state helpers ---------------------------------------------------
    _PHASES = ("waiting", "driving")
    _PASSENGER = ("boarded", "seated", "departed")
    _WOMAN = ("standing", "assisted", "unassisted")

    def _states(self):
        for ph in self._PHASES:
            for ps in self._PASSENGER:
                for ws in self._WOMAN:
                    yield (ph, ps, ws)

    # --- interface -------------------------------------------------------
    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        s0 = ("waiting", "boarded", "standing")
        o0 = ("curb", "boarded")
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[1] == "departed"

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            if s[0] == "waiting":
                return ("drive_off", "assist_woman")
            return ("continue_driving",)
        # player 1 (passenger)
        if s[1] == "boarded":
            return ("sit_down",)
        if s[1] == "seated":
            return ("request_departure",)
        return ("noop",)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if self.is_terminal(s):
            return {((s, ("none", "none")): 1.0}

        ph, ps, ws = s
        car_act, pas_act = a

        # Passenger moves first (deterministically) to settle his status.
        if ps == "boarded" and pas_act == "sit_down":
            ps = "seated"
        elif ps == "seated" and pas_act == "request_departure":
            ps = "seated"  # request handled by car below
        # else unchanged

        # Car decides departure / assistance.
        if ph == "waiting":
            if car_act == "drive_off":
                # depart only if the passenger has requested it
                if ps == "seated" and pas_act == "request_departure":
                    ph = "driving"
                    ps = "departed"
                    ws = "unassisted"
                else:
                    # cannot depart yet; nothing changes
                    pass
            elif car_act == "assist_woman":
                if ws == "standing":
                    ws = "assisted"
                # remains waiting
        else:  # driving
            # continue_driving keeps going; ride completes
            ph = "driving"
            ps = "departed"
            if ws == "standing":
                ws = "unassisted"

        ns = (ph, ps, ws)

        # Observations.
        if self.is_terminal(ns):
            o = ("none", "departed")
        else:
            car_obs = "curb" if ns[0] == "waiting" else "road"
            pas_obs = "boarded" if ns[1] == "boarded" else "seated"
            o = (car_obs, pas_obs)

        return {((ns, o)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float, ...]:
        return (0.0, 0.0)
