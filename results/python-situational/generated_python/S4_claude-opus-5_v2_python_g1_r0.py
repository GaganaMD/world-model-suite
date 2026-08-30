from posg import POSG

class ClassroomAfterTheReading(POSG):
    """A robot math teacher has read a sexist exercise description aloud; part of the
    class is giggling and part is protesting loudly.

    Players:
        0 - the robot math teacher (reads aloud from the textbook, or holds off)
        1 - the students amused by the reading (giggle, or attend)
        2 - the students objecting to the reading (protest, or attend)

    State is a pair of flags describing what the teacher currently faces:
        s[0] - amusement is being voiced in the room
        s[1] - objection is being voiced in the room

    A state with neither voiced is terminal: the room is quiet and the lesson can go on.

    Observations:
        teacher  - 'giggling_protest', 'giggling', 'protest', 'quiet'
        students - 'reading' or 'pause' (what the teacher just did)
    """

    n_players = 3

    TEACHER_ACTIONS = ('read_aloud', 'wait')
    AMUSED_ACTIONS = ('giggle', 'attend')
    OBJECTING_ACTIONS = ('protest', 'attend')

    # ---------- helpers ----------

    @staticmethod
    def _clamp(p):
        if p < 0.05:
            p = 0.05
        if p > 0.95:
            p = 0.95
        return round(p, 2)

    def _amusement_prob(self, t, g, p, gig_now):
        if g == 'giggle':
            base = 0.80 if t == 'read_aloud' else 0.50
            if gig_now:
                base += 0.05
            if p == 'protest':
                base -= 0.10
        else:
            base = 0.20 if t == 'read_aloud' else 0.10
            if gig_now:
                base += 0.10
        return self._clamp(base)

    def _objection_prob(self, t, p, g, pro_now):
        if p == 'protest':
            base = 0.85 if t == 'read_aloud' else 0.60
            if pro_now:
                base += 0.05
            if g == 'giggle':
                base += 0.05
        else:
            base = 0.25 if t == 'read_aloud' else 0.10
            if pro_now:
                base += 0.10
            if g == 'giggle':
                base += 0.05
        return self._clamp(base)

    @staticmethod
    def _teacher_obs(state):
        gig, pro = state
        if gig and pro:
            return 'giggling_protest'
        if gig:
            return 'giggling'
        if pro:
            return 'protest'
        return 'quiet'

    @staticmethod
    def _student_obs(t):
        return 'reading' if t == 'read_aloud' else 'pause'

    # ---------- interface ----------

    def initial_distribution(self):
        s0 = (True, True)
        o0 = (self._teacher_obs(s0), 'reading', 'reading')
        return {(s0, o0): 1.0}

    def is_terminal(self, s):
        return (not s[0]) and (not s[1])

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            return self.TEACHER_ACTIONS
        if i == 1:
            return self.AMUSED_ACTIONS
        return self.OBJECTING_ACTIONS

    def transition(self, s, a):
        if self.is_terminal(s):
            o = (self._teacher_obs(s), 'pause', 'pause')
            return {(s, o): 1.0}

        t, g, p = a
        gig_now, pro_now = s
        pg = self._amusement_prob(t, g, p, gig_now)
        pp = self._objection_prob(t, p, g, pro_now)
        s_obs = self._student_obs(t)

        out = {}
        for gig_next, wg in ((True, pg), (False, 1.0 - pg)):
            for pro_next, wp in ((True, pp), (False, 1.0 - pp)):
                s_next = (gig_next, pro_next)
                obs = (self._teacher_obs(s_next), s_obs, s_obs)
                out[(s_next, obs)] = out.get((s_next, obs), 0.0) + wg * wp
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
