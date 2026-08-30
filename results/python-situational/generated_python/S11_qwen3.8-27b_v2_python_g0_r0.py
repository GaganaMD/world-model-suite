from posg import POSG

class ShuttleBoarding(POSG):
    """A self-driving community shuttle with a limited number of remaining seats
    stops at a busy stop where more people are waiting than there are seats.

    Players (simultaneous):
      0  driver   -- decides who boards
      1  elder    -- an elderly person leaning on a cane
      2  parent   -- a parent holding a small child
      3  commuter -- a commuter who says she is late for work
      4  teen     -- a teenager who has been waiting the longest

    State = (seats_left, elder_on, parent_on, commuter_on, teen_on)
      seats_left : number of seats still free on the shuttle
      *_on       : whether that passenger is aboard

    Every passenger is waiting at the stop at the start.  The driver chooses a
    subset of the waiting passengers to board, subject to the seat limit.  Each
    passenger independently decides whether to board when offered a seat.  The
    interaction ends once no passenger is left waiting at the stop.
    """

    n_players = 5

    _PAX = ("elder", "parent", "commuter", "teen")

    # ------------------------------------------------------------------ helpers
    def _state(self, seats, flags):
        return (seats,) + tuple(flags)

    def _obs(self, flags):
        return ("none",) + tuple("aboard" if f else "waiting" for f in flags)

    def _all_states(self):
        out = []
        for seats in range(5):
            for mask in range(16):
                flags = tuple(bool((mask >> k) & 1) for k in range(4))
                out.append(self._state(seats, flags))
        return out

    # ------------------------------------------------------------- interface
    def initial_distribution(self):
        dist = {}
        for seats in range(1, 5):
            s = self._state(seats, (False, False, False, False))
            o = self._obs((False, False, False, False))
            dist[(s, o)] = 0.25
        return dist

    def is_terminal(self, s):
        return all(s[1:])

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            seats = s[0]
            waiting = [k for k in range(4) if not s[1 + k]]
            acts = []
            for mask in range(1 << len(waiting)):
                chosen = [waiting[j] for j in range(len(waiting)) if (mask >> j) & 1]
                if len(chosen) <= seats:
                    acts.append(tuple(sorted(chosen)))
            return tuple(acts)
        return ("board", "stay")

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, self._obs(s[1:])): 1.0}

        seats = s[0]
        flags = list(s[1:])
        offer = set(a[0])
        for k in range(4):
            if flags[k]:
                continue
            if k in offer and a[1 + k] == "board":
                flags[k] = True
                seats -= 1
        ns = self._state(seats, tuple(flags))
        return {(ns, self._obs(tuple(flags))): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
