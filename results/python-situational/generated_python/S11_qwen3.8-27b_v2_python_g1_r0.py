from posg import POSG

from collections.abc import Mapping, Sequence


class ShuttleBoarding(POSG):
    """A self-driving community shuttle stops at a busy stop with fewer seats than
    waiting passengers.  Four people are waiting, each with a distinct reason for
    wanting to board, and the driver decides who gets the remaining seats.

    Players (n_players = 5):
      0  driver   -- chooses which passengers to seat
      1  elder    -- an elderly person leaning on a cane
      2  parent   -- a parent holding a small child
      3  commuter -- a commuter who says she is late for work
      4  teen     -- a teenager who has been waiting the longest

    State tuple (s):
      (seats_left, elder_in, parent_in, commuter_in, teen_in, boarded)
        seats_left   -- number of seats still open on the shuttle
        *_in         -- whether that passenger is currently seated
        boarded      -- True once the shuttle has departed (terminal)

    Every passenger is waiting at the start, so the only thing that changes during
    boarding is how many seats remain and who is seated.  The driver acts alone;
    the passengers have no action of their own and receive the singleton `noop`.
    """

    n_players = 5

    # ---- helpers -----------------------------------------------------------

    @staticmethod
    def _seats_left(s):
        return s[0]

    @staticmethod
    def _flags(s):
        return (s[1], s[2], s[3], s[4])

    @staticmethod
    def _set_flag(flags, idx, val):
        lst = list(flags)
        lst[idx] = val
        return tuple(lst)

    def _passenger_obs(self, s, i):
        # passenger i is index i-1 in the flag block
        return "seated" if s[i] else "waiting"

    def _driver_obs(self, s):
        return "departed" if s[5] else "boarding"

    def _obs_profile(self, s):
        return (
            self._driver_obs(s),
            self._passenger_obs(s, 1),
            self._passenger_obs(s, 2),
            self._passenger_obs(s, 3),
            self._passenger_obs(s, 4),
        )

    # ---- POSG interface ----------------------------------------------------

    def initial_distribution(self):
        # Two seats remain; nobody is seated yet; the shuttle has not departed.
        s0 = (2, False, False, False, False, False)
        return {(s0, self._obs_profile(s0)): 1.0}

    def is_terminal(self, s):
        return s[5]

    def legal_actions(self, s, i):
        if i != 0:
            return ("noop",)
        if s[5]:
            return ("noop",)
        if s[0] == 0:
            return ("depart",)
        return ("seat_elder", "seat_parent", "seat_commuter", "seat_teen", "depart")

    def transition(self, s, a):
        if s[5]:
            return {(s, self._obs_profile(s)): 1.0}
        act = a[0]
        if act == "depart":
            ns = (s[0], s[1], s[2], s[3], s[4], True)
            return {(ns, self._obs_profile(ns)): 1.0}
        mapping = {
            "seat_elder": 1,
            "seat_parent": 2,
            "seat_commuter": 3,
            "seat_teen": 4,
        }
        idx = mapping[act]
        flags = self._set_flag(self._flags(s), idx, True)
        ns = (s[0] - 1, flags[0], flags[1], flags[2], flags[3], False)
        return {(ns, self._obs_profile(ns)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
