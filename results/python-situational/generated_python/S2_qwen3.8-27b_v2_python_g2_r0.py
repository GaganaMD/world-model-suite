from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple


class POSG(ABC, Generic[S, A, O]):
    pass


class HouseholdRobotDelivery(POSG):
    """
    Player 0: household robot
    Player 1: delivery boy

    State tuple: (phase, package_condition, van_position)
      phase: 'handover' | 'resolved'
      package_condition: 'rattling' | 'settled'
      van_position: 'blocking' | 'cleared'

    Terminal when phase == 'resolved'.
    """

    n_players = 2

    # --- helpers -----------------------------------------------------------

    def _obs(self, s, i):
        phase, cond, van = s
        if i == 0:
            # robot sees the package condition and the van position
            return f"{cond}_{van}"
        else:
            # delivery boy sees the van position
            return van

    # --- required methods --------------------------------------------------

    def initial_distribution(self):
        s0 = ('handover', 'rattling', 'blocking')
        o0 = (self._obs(s0, 0), self._obs(s0, 1))
        return {(s0, o0): 1.0}

    def is_terminal(self, s):
        return s[0] == 'resolved'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            return ('inspect', 'settle')
        else:
            return ('move_van', 'stay')

    def transition(self, s, a):
        if self.is_terminal(s):
            o = (self._obs(s, 0), self._obs(s, 1))
            return {(s, o): 1.0}

        phase, cond, van = s
        a_robot, a_boy = a

        # Robot effect on package condition
        if a_robot == 'inspect':
            new_cond = cond
        elif a_robot == 'settle':
            new_cond = 'settled'
        else:
            new_cond = cond

        # Boy effect on van position
        if a_boy == 'move_van':
            new_van = 'cleared'
        elif a_boy == 'stay':
            new_van = van
        else:
            new_van = van

        new_phase = 'resolved'
        ns = (new_phase, new_cond, new_van)
        o = (self._obs(ns, 0), self._obs(ns, 1))
        return {(ns, o): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
