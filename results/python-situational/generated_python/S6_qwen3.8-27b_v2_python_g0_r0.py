from posg import POSG

class POSG(POSG):
    """Two-player POSG: an elder-care robot and its resident.

    Player 0 = robot.  Player 1 = resident.

    State tuple (phase, taken):
      phase : 'due' | 'refused' | 'taken' | 'left'
              - 'due'     : medication is overdue and the resident has not yet been addressed
              - 'refused' : the resident has declined and turned away
              - 'taken'   : the resident has taken the medication
              - 'left'    : the resident has not taken it and the matter is closed
      taken : 0 | 1
              - 0 : the medication has not been taken
              - 1 : the medication has been taken

    Terminal states are ('taken', 1) and ('left', 0).
    """

    n_players = 2

    # ---- helpers -----------------------------------------------------------
    def _obs(self, s):
        phase, taken = s
        if phase == 'due':
            return ('overdue', 'not_taken')
        if phase == 'refused':
            return ('declined', 'not_taken')
        if phase == 'taken':
            return ('taken', 'taken')
        # left
        return ('closed', 'not_taken')

    # ---- interface ---------------------------------------------------------
    def initial_distribution(self):
        s = ('due', 0)
        return {((s, self._obs(s))): 1.0}

    def is_terminal(self, s):
        return s in (('taken', 1), ('left', 0))

    def legal_actions(self, s, i):
        phase, taken = s
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:  # robot
            if phase == 'due':
                return ('remind',)
            if phase == 'refused':
                return ('press', 'leave')
            return ('noop',)
        # i == 1  # resident
        if phase == 'due':
            return ('take', 'refuse')
        if phase == 'refused':
            return ('take', 'hold')
        return ('noop',)

    def transition(self, s, a):
        phase, taken = s
        robot_a, res_a = a
        if self.is_terminal(s):
            return {((s, self._obs(s))): 1.0}

        if phase == 'due':
            if res_a == 'take':
                ns = ('taken', 1)
            else:  # refuse
                ns = ('refused', 0)
            return {((ns, self._obs(ns))): 1.0}

        if phase == 'refused':
            if res_a == 'take':
                ns = ('taken', 1)
            else:  # hold
                if robot_a == 'press':
                    ns = ('refused', 0)
                else:  # leave
                    ns = ('left', 0)
            return {((ns, self._obs(ns))): 1.0}

        # phase in {'taken','left'} but not terminal (defensive)
        return {((s, self._obs(s))): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
