from posg import POSG

from typing import Mapping, Sequence, Tuple, Iterator


class POSG(ABC, Generic[S, A, O]):
    pass


class CareDecision(POSG):
    """
    Player 0: the man (decides whether to go to the gathering or stay home).
    Player 1: the care robot (accompanies the man or stays home).

    State tuple: (man_wants_to_go, man_is_tired, daughter_says_stay, son_offers_gathering)
      - man_wants_to_go: bool, whether the man expresses desire to attend the gathering
      - man_is_tired: bool, whether the man appears tired
      - daughter_says_stay: bool, whether the daughter advises staying home
      - son_offers_gathering: bool, whether the son offers to take him to the gathering

    Terminal state: (False, False, False, False) represents the decision having been made
    and the interaction concluding.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        # The situation describes a specific scenario: man wants to go, is tired,
        # daughter says stay, son offers gathering
        s = (True, True, True, True)
        o = ("wants_to_go", "tired")
        return {(s, o): 1.0}

    def is_terminal(self, s: S) -> bool:
        # Terminal when the decision is resolved
        return s == (False, False, False, False)

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            # The man decides: go to gathering or stay home
            return ("go", "stay")
        else:
            # The robot decides: accompany or stay home
            return ("accompany", "stay_home")

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        if self.is_terminal(s):
            return {((False, False, False, False), ("none", "none")): 1.0}

        man_action, robot_action = a

        # Determine the outcome based on the man's decision
        if man_action == "go":
            # Man goes to the gathering
            if robot_action == "accompany":
                # Robot accompanies
                next_s = (False, False, False, False)
                obs_man = "went_with_robot"
                obs_robot = "accompanied"
            else:
                # Robot stays home, man goes alone
                next_s = (False, False, False, False)
                obs_man = "went_alone"
                obs_robot = "stayed_home"
        else:
            # Man stays home
            if robot_action == "accompany":
                # Robot stays with him at home
                next_s = (False, False, False, False)
                obs_man = "stayed_with_robot"
                obs_robot = "stayed_with_him"
            else:
                # Robot also stays home (effectively same as accompanying in terms of location)
                next_s = (False, False, False, False)
                obs_man = "stayed_alone"
                obs_robot = "stayed_home"

        return {((next_s, (obs_man, obs_robot))): 1.0}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, float]:
        return (0.0, 0.0)
