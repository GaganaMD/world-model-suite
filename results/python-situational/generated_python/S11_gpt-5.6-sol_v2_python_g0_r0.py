from posg import POSG

class ShuttleStopPOSG(POSG):
    """Players: 0 shuttle, 1 elderly person, 2 parent, 3 commuter, 4 teenager.

    The state's sole coordinate is the pull-up condition:
    "before_pull_up", "during_pull_up", or "after_pull_up".
    """

    n_players = 5

    def initial_distribution(self):
        state = ("before_pull_up",)
        observations = ("before_pull_up",) * self.n_players
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("after_pull_up",)

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "before_pull_up":
            if i == 0:
                return ("noop",)
            return ("wait",)

        if condition == "during_pull_up":
            actions = (
                ("pull_up",),
                ("lean",),
                ("hold",),
                ("say",),
                ("noop",),
            )
            return actions[i]

        return ("noop",)

    def transition(self, s, a):
        condition = s[0]

        if condition == "before_pull_up":
            expected = ("noop", "wait", "wait", "wait", "wait")
            if a != expected:
                raise ValueError("illegal action profile")
            state_next = ("during_pull_up",)
            observations = ("during_pull_up",) * self.n_players
            return {(state_next, observations): 1.0}

        if condition == "during_pull_up":
            expected = ("pull_up", "lean", "hold", "say", "noop")
            if a != expected:
                raise ValueError("illegal action profile")
            state_next = ("after_pull_up",)
            observations = ("after_pull_up",) * self.n_players
            return {(state_next, observations): 1.0}

        if condition == "after_pull_up":
            if a != ("noop",) * self.n_players:
                raise ValueError("illegal action profile")
            observations = ("after_pull_up",) * self.n_players
            return {(s, observations): 1.0}

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0,) * self.n_players
