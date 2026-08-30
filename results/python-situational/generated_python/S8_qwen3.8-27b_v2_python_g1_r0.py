from posg import POSG

from collections.abc import Mapping, Sequence


class LockoutObservation(POSG):
    """Two-player simultaneous-move POSG of a safety-lockout lapse.

    Player 0 is the factory robot (observer/actor); player 1 is the human
    coworker.

    State tuple: (phase, lockout_done, incident)
      phase         'observing' | 'responding' | 'done'
      lockout_done  False | True   (whether the required lockout was performed)
      incident      False | True   (whether an incident occurred)

    Terminal when phase == 'done'.
    """

    n_players = 2

    # --- helpers -----------------------------------------------------------

    def _obs(self, s):
        phase, lockout_done, incident = s
        if phase == "observing":
            return ("lapse", "none")
        if phase == "responding":
            return ("lapse", "none")
        # done
        if incident:
            return ("incident", "incident")
        return ("no_incident", "no_incident")

    def _legal(self, s, i):
        phase = s[0]
        if phase == "observing":
            if i == 0:
                return ("alert", "ignore")
            return ("noop",)
        if phase == "responding":
            if i == 0:
                return ("noop",)
            return ("noop",)
        # done
        return ("noop",)

    # --- POSG interface ----------------------------------------------------

    def initial_distribution(self):
        s = ("observing", False, False)
        return {((s, self._obs(s))): 1.0}

    def is_terminal(self, s):
        return s[0] == "done"

    def legal_actions(self, s, i):
        return self._legal(s, i)

    def transition(self, s, a):
        phase, lockout_done, incident = s
        if phase == "observing":
            alert = a[0] == "alert"
            if alert:
                s_next = ("responding", True, False)
            else:
                s_next = ("responding", False, False)
            return {((s_next, self._obs(s_next))): 1.0}
        if phase == "responding":
            if lockout_done:
                s_next = ("done", True, False)
            else:
                s_next = ("done", False, True)
            return {((s_next, self._obs(s_next))): 1.0}
        # done
        return {((s, self._obs(s))): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
