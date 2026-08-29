from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class CareRobotDecision(POSG):
    """
    Players:
      0: care_robot
      1: daughter
      2: son
      3: man

    State tuple: (man_condition, decision_status)
      man_condition: 'tired' | 'rested'
      decision_status: 'undecided' | 'going_out' | 'staying_home'

    Terminal states: ('tired', 'going_out'), ('rested', 'going_out'),
                     ('tired', 'staying_home'), ('rested', 'staying_home')
    """
    n_players = 4

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str, str, str]], float]:
        # Initial state: man is tired, decision is undecided
        # Observations:
        #   care_robot sees man_condition
        #   daughter sees her own stance (stay)
        #   son sees his own stance (go)
        #   man sees his own desire (go) and condition
        s0 = ('tired', 'undecided')
        o0 = ('tired', 'stay', 'go', 'want_go_tired')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[1] in ('going_out', 'staying_home')

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            return ('noop',)
        elif i == 1:
            return ('advocate_stay', 'advocate_go')
        elif i == 2:
            return ('advocate_go', 'advocate_stay')
        elif i == 3:
            return ('choose_go', 'choose_stay')
        else:
            return ('noop',)

    def transition(self, s: S, a: Tuple[str, str, str, str]) -> Mapping[Tuple[S, Tuple[str, str, str, str]], float]:
        if self.is_terminal(s):
            o = ('none', 'none', 'none', 'none')
            return {((s[0], s[1]), o): 1.0}

        man_condition = s[0]
        _, daughter_action, son_action, man_action = a

        # Determine the decision based on the man's choice
        if man_action == 'choose_go':
            new_decision = 'going_out'
        else:
            new_decision = 'staying_home'

        # If going out while tired, there is a chance he rests up (recovers) before leaving
        # If staying home, he rests and recovers
        # For simplicity, let's model the condition change:
        # - If staying home: becomes rested
        # - If going out: remains tired (or maybe recovers slightly? Let's keep it simple: stays tired if going out immediately)
        
        if new_decision == 'staying_home':
            new_condition = 'rested'
        else:
            new_condition = man_condition

        s_next = (new_condition, new_decision)

        # Observations in terminal state
        # care_robot sees final condition
        # daughter sees final decision
        # son sees final decision
        # man sees final decision and condition
        o_robot = new_condition
        o_daughter = new_decision
        o_son = new_decision
        o_man = f"{new_decision}_{new_condition}"

        o_next = (o_robot, o_daughter, o_son, o_man)

        return {((s_next, o_next)): 1.0}

    def rewards(self, s: S, a: Tuple[str, str, str, str], s_next: S) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, 0.0, 0.0)
