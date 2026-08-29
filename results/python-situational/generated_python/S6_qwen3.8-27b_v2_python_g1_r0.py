from posg import POSG

from collections.abc import Mapping, Sequence


class POSG(ABC, Generic[S, A, O]):
    """Elder-care medication reminder.

    Player 0: the elder-care robot.
    Player 1: the resident.

    State tuple (phase, resident_stance):
      phase: 'due' | 'refused' | 'taken' | 'declined'
      resident_stance: 'unaware' | 'resistant' | 'accepting' | 'settled'

    Terminal phases: 'taken' and 'declined'.
    """
    n_players = 2

    # ---- helpers ---------------------------------------------------------
    def _obs(self, s):
        phase, stance = s
        if phase == 'due':
            return ('medication_due', 'no_reminder')
        if phase == 'refused':
            return ('resident_refused', 'resident_refused')
        if phase == 'taken':
            return ('medication_taken', 'medication_taken')
        if phase == 'declined':
            return ('medication_declined', 'medication_declined')
        return ('none', 'none')

    # ---- required methods ------------------------------------------------
    def initial_distribution(self) -> Mapping[tuple[S, tuple[str, str]], float]:
        s = ('due', 'unaware')
        return {((s, self._obs(s))): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] in ('taken', 'declined')

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        phase = s[0]
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            if phase == 'due':
                return ('remind',)
            if phase == 'refused':
                return ('remind_again', 'leave_alone')
            return ('noop',)
        # i == 1
        if phase == 'due':
            return ('take_medication', 'refuse')
        if phase == 'refused':
            return ('take_medication', 'keep_refusing')
        return ('noop',)

    def transition(self, s: S, a: tuple[str, str]) -> Mapping[tuple[S, tuple[str, str]], float]:
        phase, stance = s
        r_act, res_act = a

        if phase == 'due':
            if res_act == 'take_medication':
                ns = ('taken', 'settled')
            else:  # refuse
                ns = ('refused', 'resistant')
            return {((ns, self._obs(ns))): 1.0}

        if phase == 'refused':
            if res_act == 'take_medication':
                ns = ('taken', 'settled')
            elif r_act == 'leave_alone':
                ns = ('declined', 'settled')
            else:  # remind_again + keep_refusing
                ns = ('refused', 'resistant')
            return {((ns, self._obs(ns))): 1.0}

        # terminal
        return {((s, self._obs(s))): 1.0}

    def rewards(self, s: S, a: tuple[str, str], s_next: S) -> tuple[float, float]:
        return (0.0, 0.0)
