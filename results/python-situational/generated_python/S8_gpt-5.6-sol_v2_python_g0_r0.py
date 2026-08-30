from posg import POSG

class FactoryLockoutPOSG(POSG):
    """Player 0 is the factory robot; player 1 is the human coworker.

    Each state is a one-coordinate tuple recording the current condition:
    lockout_required, lockout_skipped, or reach_performed.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("lockout_required",), ("none", "none")): 1.0
        }

    def is_terminal(self, s):
        return s == ("reach_performed",)

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("invalid player index")

        if s == ("lockout_required",):
            return ("observe",) if i == 0 else ("skip_lockout",)

        if s == ("lockout_skipped",):
            return ("noop",) if i == 0 else ("reach_into_machine",)

        if s == ("reach_performed",):
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        if s == ("lockout_required",):
            if a != ("observe", "skip_lockout"):
                raise ValueError("illegal action profile")
            return {
                (("lockout_skipped",), ("lockout_skipped", "none")): 1.0
            }

        if s == ("lockout_skipped",):
            if a != ("noop", "reach_into_machine"):
                raise ValueError("illegal action profile")
            return {
                (("reach_performed",), ("none", "none")): 1.0
            }

        if s == ("reach_performed",):
            if a != ("noop", "noop"):
                raise ValueError("illegal action profile")
            return {
                (("reach_performed",), ("none", "none")): 1.0
            }

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
