from posg import POSG

class ShuttleStopPOSG(POSG):
    """Player 0 is the self-driving shuttle; players 1 through 4 are,
    respectively, the elderly person, parent, commuter, and teenager.

    Each state is a one-coordinate tuple recording whether arrival is pending
    or has occurred.
    """

    n_players = 5

    def initial_distribution(self):
        state = ("arrival_pending",)
        observations = ("none", "none", "none", "none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("arrival_occurred",)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        actions = (
            ("drive", "pull_up"),
            ("wait", "lean"),
            ("wait", "hold"),
            ("wait", "say_late"),
            ("wait",),
        )
        return actions[i]

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none", "none", "none", "none")): 1.0}

        shuttle_observation = "driving" if a[0] == "drive" else "arrival"
        elderly_observation = "waiting" if a[1] == "wait" else "leaning"
        parent_observation = "waiting" if a[2] == "wait" else "holding"
        commuter_observation = "waiting" if a[3] == "wait" else "speaking"
        teenager_observation = "waiting"

        observations = (
            shuttle_observation,
            elderly_observation,
            parent_observation,
            commuter_observation,
            teenager_observation,
        )
        next_state = (
            ("arrival_pending",) if a[0] == "drive"
            else ("arrival_occurred",)
        )
        return {(next_state, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
