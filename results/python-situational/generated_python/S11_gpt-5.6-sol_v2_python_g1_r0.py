from posg import POSG

class ShuttleStopPOSG(POSG):
    """Players: 0 is the shuttle, 1 the cane user, 2 the parent,
    3 the commuter, and 4 the teenager. The state coordinate records
    whether the shuttle's pull-up act is pending or complete.
    """

    n_players = 5

    def initial_distribution(self):
        state = ("pull_up_pending",)
        observations = ("none", "none", "none", "none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("pull_up_complete",)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if s != ("pull_up_pending",):
            raise ValueError("unknown state")
        if i == 0:
            return ("pull_up",)
        if i == 1:
            return ("lean", "wait")
        if i == 2:
            return ("hold", "wait")
        if i == 3:
            return ("say", "wait")
        if i == 4:
            return ("wait",)
        raise IndexError("unknown player")

    def transition(self, s, a):
        if len(a) != self.n_players:
            raise ValueError("invalid action profile")

        if self.is_terminal(s):
            if a != ("noop", "noop", "noop", "noop", "noop"):
                raise ValueError("illegal action profile")
            observations = ("none", "none", "none", "none", "none")
            return {(s, observations): 1.0}

        if s != ("pull_up_pending",):
            raise ValueError("unknown state")

        for i, action in enumerate(a):
            if action not in self.legal_actions(s, i):
                raise ValueError("illegal action profile")

        observed_acts = "_".join(a[1:])
        observations = (
            observed_acts,
            observed_acts,
            observed_acts,
            observed_acts,
            observed_acts,
        )
        return {(("pull_up_complete",), observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
