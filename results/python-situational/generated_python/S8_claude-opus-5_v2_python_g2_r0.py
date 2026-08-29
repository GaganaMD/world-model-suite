from posg import POSG

PENDING = "lockout_pending"
DONE = "lockout_done"
SKIPPED = "lockout_skipped"
INCIDENT = "incident"
COMPLETE = "reach_complete"


class SafetyLockoutSkip(POSG):
    """Robot bystander and human coworker at a machine that requires a safety lockout.

    Player 0 is the factory robot: it can attend to the coworker (`observe`),
    call out (`warn`), cut the machine (`halt`), or stay with its own task
    (`continue`).
    Player 1 is the human coworker: it can perform the lockout (`lock_out`),
    leave it undone (`skip`), reach into the machine (`reach_in`), or hold off
    (`wait`).

    A state is a one-coordinate tuple naming the standing condition:
      s[0] == PENDING   -- the lockout step is still outstanding and the
                           coworker has not committed either way;
      s[0] == DONE      -- the machine is isolated, the coworker has not
                           reached in;
      s[0] == SKIPPED   -- the machine is live with the lockout undone, the
                           coworker has not reached in;
      s[0] == COMPLETE  -- the reach is over without incident (terminal);
      s[0] == INCIDENT  -- the reach ended in an incident (terminal).

    The robot only learns the lockout condition in the steps where it attends
    to the coworker or where cutting the machine tells it whether the machine
    was live; otherwise it observes `none` in conditions it cannot tell apart.
    """

    n_players = 2

    def initial_distribution(self):
        return {((PENDING,), ("none", "none")): 1.0}

    def is_terminal(self, s):
        return s[0] in (INCIDENT, COMPLETE)

    def legal_actions(self, s, i):
        c = s[0]
        if c == PENDING:
            return ("observe", "continue") if i == 0 else ("lock_out", "skip")
        if c == DONE:
            return ("observe", "warn", "halt", "continue") if i == 0 else ("reach_in", "wait")
        if c == SKIPPED:
            if i == 0:
                return ("observe", "warn", "halt", "continue")
            return ("reach_in", "lock_out", "wait")
        return ("noop",)

    def transition(self, s, a):
        r, h = a[0], a[1]
        c = s[0]

        if c == PENDING:
            nxt = DONE if h == "lock_out" else SKIPPED
            ro = nxt if r == "observe" else "none"
            return {((nxt,), (ro, "none")): 1.0}

        if c == DONE:
            ro = {
                "observe": "lockout_done",
                "halt": "halt_issued",
                "warn": "none",
                "continue": "none",
            }[r]
            if h == "wait":
                ho = "warning" if r == "warn" else "none"
                return {((DONE,), (ro, ho)): 1.0}
            if r == "warn":
                return {
                    ((DONE,), ("none", "warning")): 0.5,
                    ((COMPLETE,), ("none", "reach_complete")): 0.5,
                }
            return {((COMPLETE,), (ro, "reach_complete")): 1.0}

        if c == SKIPPED:
            if r == "halt":
                if h == "reach_in":
                    return {
                        ((COMPLETE,), ("machine_stopped", "machine_stopped")): 0.95,
                        ((INCIDENT,), ("incident", "incident")): 0.05,
                    }
                return {((DONE,), ("machine_stopped", "machine_stopped")): 1.0}
            if h == "lock_out":
                ro = "lockout_done" if r == "observe" else "none"
                ho = "warning" if r == "warn" else "none"
                return {((DONE,), (ro, ho)): 1.0}
            if h == "wait":
                ro = "lockout_skipped" if r == "observe" else "none"
                ho = "warning" if r == "warn" else "none"
                return {((SKIPPED,), (ro, ho)): 1.0}
            if r == "warn":
                return {
                    ((SKIPPED,), ("none", "warning")): 0.5,
                    ((COMPLETE,), ("none", "reach_complete")): 0.45,
                    ((INCIDENT,), ("incident", "incident")): 0.05,
                }
            ro = "lockout_skipped" if r == "observe" else "none"
            return {
                ((COMPLETE,), (ro, "reach_complete")): 0.9,
                ((INCIDENT,), ("incident", "incident")): 0.1,
            }

        return {(s, ("none", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
