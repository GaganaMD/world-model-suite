from posg import POSG

from typing import Mapping, Sequence, Iterator, Generic, Tuple, TypeVar, Dict, List

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class HouseholdRobotDelivery(POSG):
    """
    Player 0: household robot
    Player 1: delivery boy

    State tuple: (phase, package_rattling, van_blocking_traffic)
      - phase: 'handover' | 'done'
      - package_rattling: True/False
      - van_blocking_traffic: True/False

    Terminal when phase == 'done'.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        # Robot knows owner ordered a glass vase; package rattles; van blocks traffic
        s0 = ('handover', True, True)
        o0 = ('rattling_package', 'van_blocking')
        return {((s0, o0)): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'done'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Robot can accept the package or inspect it
            return ('accept', 'inspect')
        else:
            # Delivery boy can leave (move van) or stay
            return ('leave', 'stay')

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        if self.is_terminal(s):
            return {((s, ('none', 'none'))): 1.0}

        phase, rattling, blocking = s
        robot_action, boy_action = a

        # Determine next state
        # If robot accepts, handover completes
        # If robot inspects, handover continues but robot learns about contents
        # Boy leaving clears traffic; staying keeps it blocked

        if robot_action == 'accept':
            next_phase = 'done'
        else:
            next_phase = 'handover'

        next_blocking = False if boy_action == 'leave' else True
        next_rattling = rattling  # rattling doesn't change

        next_s = (next_phase, next_rattling, next_blocking)

        # Observations
        if next_phase == 'done':
            robot_obs = 'accepted'
            boy_obs = 'left' if boy_action == 'leave' else 'stayed'
        else:
            # Robot inspecting: learns package is fragile (glass)
            robot_obs = 'fragile_contents'
            boy_obs = 'left' if boy_action == 'leave' else 'stayed'

        return {((next_s, (robot_obs, boy_obs))): 1.0}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
