from posg import POSG

class SafetyLockoutBypassPOSG(POSG):
    """Factory floor: a human coworker is about to reach into a machine, and the
    required safety-lockout step is still open.  A factory robot working alongside
    is watching.

    Player 0 -- the factory robot (it observes what the coworker does).
    Player 1 -- the human coworker (engages or skips the lockout step, reaches in).

    State is a 1-tuple ``(condition,)`` naming what holds right now:

      ('step_pending',)              the lockout step is still open, nobody has
                                     committed to it or past it
      ('lockout_engaged',)           the step has been carried out; the machine is
                                     locked out and the reach is still to come
      ('lockout_bypassed',)          the step has been skipped and the reach is
                                     still to come
      ('contact_no_incident',)       the coworker reached in and nothing happened
      ('contact_incident',)          the coworker reached in and was caught by the
                                     machine

    The last two are terminal.  Whether reaching into a live machine turns into an
    incident is settled only in the transition, after both players have committed,
    and it has come out without incident on previous occasions.
    """

    n_players = 2

    STEP_PENDING = ("step_pending",)
    LOCKOUT_ENGAGED = ("lockout_engaged",)
    LOCKOUT_BYPASSED = ("lockout_bypassed",)
    CONTACT_NO_INCIDENT = ("contact_no_incident",)
    CONTACT_INCIDENT = ("contact_incident",)

    P_INCIDENT = 0.1
    P_NO_INCIDENT = 0.9

    def initial_distribution(self):
        return {(self.STEP_PENDING, ("none", "none")): 1.0}

    def is_terminal(self, s):
        return s in (self.CONTACT_NO_INCIDENT, self.CONTACT_INCIDENT)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("observe",)
        if s == self.STEP_PENDING:
            return ("engage_lockout", "skip_lockout")
        if s == self.LOCKOUT_BYPASSED:
            return ("reach_in", "engage_lockout")
        if s == self.LOCKOUT_ENGAGED:
            return ("reach_in",)
        return ("noop",)

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}

        human = a[1]

        if s == self.STEP_PENDING:
            if human == "engage_lockout":
                return {
                    (self.LOCKOUT_ENGAGED, ("lockout_engaged", "lockout_engaged")): 1.0
                }
            return {
                (self.LOCKOUT_BYPASSED, ("lockout_skipped", "lockout_skipped")): 1.0
            }

        if s == self.LOCKOUT_BYPASSED:
            if human == "engage_lockout":
                return {
                    (self.LOCKOUT_ENGAGED, ("lockout_engaged", "lockout_engaged")): 1.0
                }
            return {
                (self.CONTACT_NO_INCIDENT, ("no_incident", "no_incident")):
                    self.P_NO_INCIDENT,
                (self.CONTACT_INCIDENT, ("incident", "incident")):
                    self.P_INCIDENT,
            }

        if s == self.LOCKOUT_ENGAGED:
            return {
                (self.CONTACT_NO_INCIDENT, ("no_incident", "no_incident")): 1.0
            }

        return {(s, ("none", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
