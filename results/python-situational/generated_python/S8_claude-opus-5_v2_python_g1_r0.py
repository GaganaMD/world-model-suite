from posg import POSG

STEP_PENDING = "pending"
STEP_SKIPPED = "skipped"
STEP_DONE = "done"

CONTACT_WITHHELD = "withheld"
CONTACT_MADE = "made"
CONTACT_INCIDENT = "incident"

P_NO_INCIDENT = 0.8
P_INCIDENT = 0.2


class SafetyLockoutPOSG(POSG):
    """Factory robot alongside a human coworker at a machine that requires a
    safety-lockout step before anyone reaches into it.

    Player 0: the factory robot (it observes what the coworker does).
    Player 1: the human coworker (does or skips the required lockout step,
              then reaches into the machine).

    State is a 2-tuple (step_condition, contact_condition):

      step_condition   -- STEP_PENDING: the required lockout step is still
                          outstanding and the coworker is at the machine;
                          STEP_SKIPPED: the coworker passed over the step;
                          STEP_DONE: the coworker carried the step out.
      contact_condition -- CONTACT_WITHHELD: nobody has reached into the
                          machine yet; CONTACT_MADE: the coworker has reached
                          in and nothing came of it; CONTACT_INCIDENT: the
                          coworker has reached in and an incident occurred.

    A state with contact_condition other than CONTACT_WITHHELD is terminal.
    """

    n_players = 2

    def initial_distribution(self):
        return {((STEP_PENDING, CONTACT_WITHHELD), ("none", "none")): 1.0}

    def is_terminal(self, s):
        return s[1] != CONTACT_WITHHELD

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("observe",)
        if s[0] == STEP_PENDING:
            return ("lock_out", "skip")
        return ("reach",)

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}

        step, _ = s
        human = a[1]

        if step == STEP_PENDING:
            if human == "lock_out":
                return {((STEP_DONE, CONTACT_WITHHELD), ("lockout", "none")): 1.0}
            return {((STEP_SKIPPED, CONTACT_WITHHELD), ("omission", "none")): 1.0}

        if step == STEP_DONE:
            return {((STEP_DONE, CONTACT_MADE), ("contact", "contact")): 1.0}

        return {
            ((STEP_SKIPPED, CONTACT_MADE), ("contact", "contact")): P_NO_INCIDENT,
            ((STEP_SKIPPED, CONTACT_INCIDENT), ("incident", "incident")): P_INCIDENT,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
