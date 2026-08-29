from posg import POSG

class ClassroomReactionPOSG(POSG):
    """Robot math teacher and the reacting class after a sexist textbook exercise is read aloud.

    Players:
        0 - the robot math teacher (reads aloud from the textbook, or holds off)
        1 - the giggling students
        2 - the protesting students

    State is a 2-tuple of booleans:
        s[0] - giggling is going on
        s[1] - protesting is going on

    The state in which neither reaction is going on is terminal.

    The teacher perceives which reactions are going on. The students, amid the
    noise, only perceive whether the teacher is reading from the textbook or
    holding off; they cannot tell apart outcomes that differ in who is still
    reacting.
    """

    n_players = 3

    TEACHER_READ = "read_aloud"
    TEACHER_HOLD = "hold_off"
    GIGGLE = "giggle"
    PROTEST = "protest"
    SETTLE = "settle"
    NOOP = "noop"

    def _teacher_obs(self, s):
        if s[0] and s[1]:
            return "giggling_and_protest"
        if s[0]:
            return "giggling"
        if s[1]:
            return "protest"
        return "settled"

    def _student_obs(self, a0):
        return "reading" if a0 == self.TEACHER_READ else "held_off"

    def _faction_next(self, active, action, reading):
        """Law over whether this faction's reaction is going on next."""
        if active:
            if action == self.SETTLE:
                if reading:
                    return {False: 0.6, True: 0.4}
                return {False: 1.0}
            return {True: 1.0}
        if reading:
            return {True: 0.5, False: 0.5}
        return {False: 1.0}

    def initial_distribution(self):
        s0 = (True, True)
        o0 = (self._teacher_obs(s0), "reading", "reading")
        return {(s0, o0): 1.0}

    def is_terminal(self, s):
        return not s[0] and not s[1]

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return (self.NOOP,)
        if i == 0:
            return (self.TEACHER_READ, self.TEACHER_HOLD)
        if i == 1:
            if s[0]:
                return (self.GIGGLE, self.SETTLE)
            return (self.NOOP,)
        if s[1]:
            return (self.PROTEST, self.SETTLE)
        return (self.NOOP,)

    def transition(self, s, a):
        if self.is_terminal(s):
            o = (self._teacher_obs(s), self._student_obs(self.TEACHER_HOLD),
                 self._student_obs(self.TEACHER_HOLD))
            return {(s, o): 1.0}

        reading = (a[0] == self.TEACHER_READ)
        gig = self._faction_next(s[0], a[1], reading)
        pro = self._faction_next(s[1], a[2], reading)
        stu_obs = self._student_obs(a[0])

        out = {}
        for g, pg in gig.items():
            for p, pp in pro.items():
                s_next = (g, p)
                o = (self._teacher_obs(s_next), stu_obs, stu_obs)
                key = (s_next, o)
                out[key] = out.get(key, 0.0) + pg * pp
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
