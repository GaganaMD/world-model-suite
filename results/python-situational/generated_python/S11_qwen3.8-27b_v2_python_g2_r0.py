from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple


class ShuttleBoarding(POSG):
    """A self-driving community shuttle with a limited number of remaining seats
    stops at a busy stop where more people are waiting than there are seats.

    Players (indices):
      0  driver   -- decides who boards
      1  elder    -- an elderly person leaning on a cane
      2  parent   -- a parent holding a small child
      3  commuter -- a commuter who says she is late for work
      4  teen     -- a teenager who has been waiting the longest

    State tuple (s):
      (seats_left, elder_on, parent_on, commuter_on, teen_on)
        seats_left   : number of seats still free on the shuttle
        *_on         : whether that passenger has boarded

    Terminal when seats_left == 0 (the shuttle departs) or all four passengers
    have boarded.
    """

    n_players = 5

    # --- helpers -----------------------------------------------------------

    def _passengers(self, s):
        return (s[1], s[2], s[3], s[4])

    def _obs(self, s, i):
        if i == 0:
            return "seats_%d" % s[0]
        if s[i] is True:
            return "aboard"
        return "waiting"

    def _profile(self, s, i):
        return (self._obs(s, 0),
                self._obs(s, 1),
                self._obs(s, 2),
                self._obs(s, 3),
                self._obs(s, 4))

    # --- POSG interface ----------------------------------------------------

    def initial_distribution(self):
        s = (1, False, False, False, False)
        return {(s, self._profile(s, 0)): 1.0}

    def is_terminal(self, s):
        return s[0] == 0 or all(self._passengers(s))

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("board_elder", "board_parent", "board_commuter",
                    "board_teen", "depart")
        if s[i]:
            return ("stay",)
        return ("request_seat",)

    def transition(self, s, a):
        if self.is_terminal(s):
            return {((s, self._profile(s, 0)), 1.0)}

        d = a[0]
        if d == "depart":
            ns = (s[0], s[1], s[2], s[3], s[4])
            return {((ns, self._profile(ns, 0)), 1.0)}

        idx = {"board_elder": 1, "board_parent": 2,
               "board_commuter": 3, "board_teen": 4}[d]
        if s[idx]:
            # requested seat already taken: nothing changes
            ns = (s[0], s[1], s[2], s[3], s[4])
            return {((ns, self._profile(ns, 0)), 1.0)}

        if s[0] <= 0:
            # no seat left: request goes unmet
            ns = (s[0], s[1], s[2], s[3], s[4])
            return {((ns, self._profile(ns, 0)), 1.0)}

        # board the chosen passenger
        flags = list(self._passengers(s))
        flags[idx - 1] = True
        ns = (s[0] - 1, flags[0], flags[1], flags[2], flags[3])
        return {((ns, self._profile(ns, 0)), 1.0)}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
