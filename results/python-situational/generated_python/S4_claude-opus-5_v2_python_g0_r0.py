from posg import POSG

OBS_TEACHER_PROTEST = "protest"
OBS_TEACHER_GIGGLING = "giggling"
OBS_TEACHER_QUIET = "quiet"

READ_ALOUD = "read_aloud"
COMMENT_ON_TEXT = "comment_on_text"
GIGGLE = "giggle"
PROTEST = "protest"
ATTEND = "attend"
NOOP = "noop"

PRESENT = "present"
ABSENT = "absent"

AMUSEMENT_PERSISTS = {
    (GIGGLE, READ_ALOUD): 0.8,
    (GIGGLE, COMMENT_ON_TEXT): 0.6,
    (ATTEND, READ_ALOUD): 0.2,
    (ATTEND, COMMENT_ON_TEXT): 0.1,
}

OBJECTION_PERSISTS = {
    (PROTEST, READ_ALOUD): 0.9,
    (PROTEST, COMMENT_ON_TEXT): 0.6,
    (ATTEND, READ_ALOUD): 0.3,
    (ATTEND, COMMENT_ON_TEXT): 0.1,
}


class ClassroomAfterTheReading(POSG):
    """A robot math teacher and a class split by the passage it has just read aloud.

    Player 0: the robot math teacher.  It either goes on reading aloud from the
      textbook or speaks about the description it has just read.
    Player 1: the students who are giggling.  They keep giggling or attend.
    Player 2: the students who are protesting loudly.  They keep protesting or
      attend.

    State is a pair of reaction conditions the teacher faces:
      s[0]: amusement in the room -- "present" or "absent"
      s[1]: objection in the room -- "present" or "absent"
    The state in which neither holds is terminal: the class is attending and the
    lesson runs on.

    Teacher observation: "protest" whenever objection is in the room (loud noise
    covers everything else), "giggling" when only amusement is, "quiet"
    otherwise.  Student observation: what the teacher just said.
    """

    n_players = 3

    def initial_distribution(self):
        return {
            ((PRESENT, PRESENT), (OBS_TEACHER_PROTEST, READ_ALOUD, READ_ALOUD)): 1.0
        }

    def is_terminal(self, s):
        return s == (ABSENT, ABSENT)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return (NOOP,)
        if i == 0:
            return (READ_ALOUD, COMMENT_ON_TEXT)
        if i == 1:
            return (GIGGLE, ATTEND)
        return (PROTEST, ATTEND)

    def _teacher_obs(self, s_next):
        if s_next[1] == PRESENT:
            return OBS_TEACHER_PROTEST
        if s_next[0] == PRESENT:
            return OBS_TEACHER_GIGGLING
        return OBS_TEACHER_QUIET

    def transition(self, s, a):
        teacher_act, amused_act, objecting_act = a[0], a[1], a[2]
        pa = AMUSEMENT_PERSISTS[(amused_act, teacher_act)]
        po = OBJECTION_PERSISTS[(objecting_act, teacher_act)]

        entries = []
        for amusement, p_am in ((PRESENT, pa), (ABSENT, 1.0 - pa)):
            for objection, p_ob in ((PRESENT, po), (ABSENT, 1.0 - po)):
                s_next = (amusement, objection)
                obs = (self._teacher_obs(s_next), teacher_act, teacher_act)
                entries.append(((s_next, obs), p_am * p_ob))

        entries.sort(key=lambda kv: -kv[1])
        out = {}
        for key, p in entries[1:]:
            out[key] = p
        out[entries[0][0]] = 1.0 - sum(out.values())
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
