from posg import POSG

from collections import defaultdict


class ShuttleBoarding(POSG):
    """
    Player 0: driver
    Player 1: elderly person
    Player 2: parent
    Player 3: commuter
    Player 4: teenager

    State tuple: (phase, elder_boarded, parent_boarded, commuter_boarded, teen_boarded)
      phase: 0 = boarding, 1 = departed
      booleans: whether each person has boarded
    """
    n_players = 5

    def initial_distribution(self):
        s0 = (0, False, False, False, False)
        o0 = ("boarding", "waiting", "waiting", "waiting", "waiting")
        return {(s0, o0): 1.0}

    def is_terminal(self, s):
        return s[0] == 1

    def legal_actions(self, s, i):
        if s[0] == 1:
            return ("noop",)
        if i == 0:
            return ("board_elder", "board_parent", "board_commuter", "board_teen", "depart")
        else:
            return ("request_seat",)

    def _obs_profile(self, s):
        phase = s[0]
        if phase == 1:
            return ("departed", "on_board", "on_board", "on_board", "on_board")
        # phase 0
        obs = ["boarding"]
        for j in range(1, 5):
            if s[j]:
                obs.append("on_board")
            else:
                obs.append("waiting")
        return tuple(obs)

    def transition(self, s, a):
        if s[0] == 1:
            o = self._obs_profile(s)
            return {(s, o): 1.0}

        driver_action = a[0]
        new_s = list(s)
        new_s[0] = 1  # always depart after this step

        if driver_action == "board_elder":
            new_s[1] = True
        elif driver_action == "board_parent":
            new_s[2] = True
        elif driver_action == "board_commuter":
            new_s[3] = True
        elif driver_action == "board_teen":
            new_s[4] = True
        # depart: no one boards

        new_s = tuple(new_s)
        o = self._obs_profile(new_s)
        return {(new_s, o): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
