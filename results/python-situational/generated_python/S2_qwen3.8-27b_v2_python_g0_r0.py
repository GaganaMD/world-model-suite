from posg import POSG

class VaseDelivery(POSG):
    """Two-player simultaneous-move POSG.

    Player 0 = household robot.
    Player 1 = delivery boy.

    State tuple (phase, intact, accepted):
      phase     : 'handoff' | 'depart' | 'done'
      intact    : True/False  -- whether the vase inside the package is undamaged
      accepted  : True/False  -- whether the robot has taken the package

    Observations:
      robot : 'rattle' | 'quiet' | 'none'
      boy   : 'blocking' | 'gone' | 'none'
    """
    n_players = 2

    # --- helpers ---------------------------------------------------------
    def _obs(self, s):
        phase, intact, accepted = s
        if phase == 'handoff':
            r = 'rattle' if not intact else 'quiet'
            b = 'blocking'
        elif phase == 'depart':
            r = 'none'
            b = 'blocking'
        else:
            r = 'none'
            b = 'gone'
        return (r, b)

    def _actions(self, s):
        phase, intact, accepted = s
        if phase == 'handoff':
            return ('inspect', 'accept'), ('leave',)
        if phase == 'depart':
            return ('noop',), ('drive_off',)
        return ('noop',), ('noop',)

    # --- required methods ------------------------------------------------
    def initial_distribution(self):
        s0 = ('handoff', False, False)
        return {((s0), self._obs(s0)): 1.0}

    def is_terminal(self, s):
        return s[0] == 'done'

    def legal_actions(self, s, i):
        return self._actions(s)[i]

    def transition(self, s, a):
        phase, intact, accepted = s
        ra, ba = a
        if phase == 'handoff':
            if ra == 'inspect':
                ns = ('handoff', intact, False)
                return {((ns), self._obs(ns)): 1.0}
            # accept
            if ba == 'leave':
                ns = ('handoff', intact, False)
                return {((ns), self._obs(ns)): 1.0}
            # accept + leave -> depart
            ns = ('depart', intact, True)
            return {((ns), self._obs(ns)): 1.0}
        if phase == 'depart':
            if ba == 'drive_off':
                ns = ('done', intact, True)
                return {((ns), self._obs(ns)): 1.0}
            ns = ('depart', intact, True)
            return {((ns), self._obs(ns)): 1.0}
        # done
        ns = s
        return {((ns), self._obs(ns)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
