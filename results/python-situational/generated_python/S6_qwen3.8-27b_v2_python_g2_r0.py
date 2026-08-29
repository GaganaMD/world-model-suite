from posg import POSG

class MedicationReminder(POSG):
    """Two-player POSG: an elder-care robot and its resident over an overdue dose.

    Player 0 = robot.  Player 1 = resident.

    State tuple (phase, refusal):
      phase   : 'due' | 'reminded' | 'taken' | 'declined'
      refusal : False | True   (whether the resident has refused)

    Terminal states: ('taken', False) and ('declined', True).
    """

    n_players = 2

    # ---- states -------------------------------------------------------------
    DUE = ('due', False)
    REMINDED = ('reminded', True)
    TAKEN = ('taken', False)
    DECLINED = ('declined', True)

    _TERMINAL = frozenset({TAKEN, DECLINED})

    # ---- actions ------------------------------------------------------------
    NOOP = 'noop'
    REMIND = 'remind'
    TAKE = 'take'
    REFUSE = 'refuse'

    # ---- observations -------------------------------------------------------
    OBS_DUE = 'due'
    OBS_REMINDED = 'reminded'
    OBS_TAKEN = 'taken'
    OBS_DECLINED = 'declined'

    def is_terminal(self, s):
        return s in self._TERMINAL

    def initial_distribution(self):
        return {
            (self.DUE, (self.OBS_DUE, self.OBS_DUE)): 1.0,
        }

    def legal_actions(self, s, i):
        if s in self._TERMINAL:
            return (self.NOOP,)
        if i == 0:
            if s == self.DUE:
                return (self.REMIND,)
            return (self.NOOP,)
        # i == 1
        if s == self.DUE:
            return (self.NOOP,)
        if s == self.REMINDED:
            return (self.TAKE, self.REFUSE)
        return (self.NOOP,)

    def transition(self, s, a):
        if s in self._TERMINAL:
            return {(s, (self.OBS_TAKEN if s == self.TAKEN else self.OBS_DECLINED,
                         self.OBS_TAKEN if s == self.TAKEN else self.OBS_DECLINED)): 1.0}

        if s == self.DUE:
            # robot reminds; resident turns away and refuses
            return {(self.REMINDED, (self.OBS_REMINDED, self.OBS_REMINDED)): 1.0}

        if s == self.REMINDED:
            if a[1] == self.TAKE:
                return {(self.TAKEN, (self.OBS_TAKEN, self.OBS_TAKEN)): 1.0}
            return {(self.DECLINED, (self.OBS_DECLINED, self.OBS_DECLINED)): 1.0}

        raise ValueError('unreachable state %r' % (s,))

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
