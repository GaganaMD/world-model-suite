from posg import POSG

class FactoryLockoutPOSG(POSG):
    """Player 0 is the factory robot; player 1 is the human coworker.

    The state is a one-coordinate tuple describing the current condition:
    "lockout_pending" means the lockout step can be skipped,
    "reach_available" means the step has been skipped and reaching can occur,
    and "reached" means the interaction has ended.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("lockout_pending",), ("none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("reached",)

    def legal_actions(self, s, i):
        if s == ("lockout_pending",):
            return ("observe",) if i == 0 else ("skip_lockout",)
        if s == ("reach_available",):
            return ("noop",) if i == 0 else ("reach",)
        return ("noop",)

    def transition(self, s, a):
        if s == ("lockout_pending",):
            return {
                (("reach_available",), ("skip_seen", "none")): 1.0
            }
        if s == ("reach_available",):
            return {
                (("reached",), ("reach_seen", "none")): 1.0
            }
        return {
            (("reached",), ("none", "none")): 1.0
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
