from posg import POSG

FATIGUE = "fatigue"
STEADY = "steady"

OPEN = "open"
ASSESSED = "assessed"
OUTING = "outing"
RESTING = "resting"

_P_OUT_STEADY = {-3: 0.15, -2: 0.28, -1: 0.42, 0: 0.60, 1: 0.75, 2: 0.86, 3: 0.94}
_P_OUT_FATIGUE = {-3: 0.05, -2: 0.12, -1: 0.22, 0: 0.38, 1: 0.55, 2: 0.70, 3: 0.82}

Q_SETTLE = 0.3


class HomeRecoveryOutingPOSG(POSG):
    """Conflicting voices around a man recovering at home.

    Players:
        0 - the care robot looking after him
        1 - the elderly man himself
        2 - the daughter who lives with him
        3 - the visiting son

    State is a 2-tuple (condition, stage):
        condition - his underlying state of fatigue, not settled by anyone's
                    word: FATIGUE or STEADY.  Hidden at the outset; the robot
                    can bring it into the open by attending to him.
        stage     - OPEN     : the matter is still being pressed, nothing
                               about his condition has been established
                    ASSESSED : the robot has established his condition, the
                               matter is still being pressed
                    OUTING   : he has gone to the gathering (terminal)
                    RESTING  : he has stayed home to rest (terminal)

    Observations: 'looks_tired' (his visible tiredness), 'assessment' (he is
    being attended to, without the finding), 'fatigue' / 'steady' (the finding
    itself, seen only by the robot), 'outing' / 'resting' (how it settled),
    'none'.
    """

    n_players = 4

    def initial_distribution(self):
        obs = ("looks_tired", "none", "looks_tired", "looks_tired")
        return {
            ((FATIGUE, OPEN), obs): 0.5,
            ((STEADY, OPEN), obs): 0.5,
        }

    def is_terminal(self, s):
        return s[1] in (OUTING, RESTING)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            if s[1] == OPEN:
                return ("check", "support_rest", "support_outing")
            return ("support_rest", "support_outing")
        if i == 1:
            return ("ask_to_go", "rest")
        if i == 2:
            return ("urge_rest", "defer")
        return ("offer_outing", "defer")

    def _pressure(self, s, a):
        diff = 0
        diff += 1 if a[1] == "ask_to_go" else -1
        if a[2] == "urge_rest":
            diff -= 1
        if a[3] == "offer_outing":
            diff += 1
        if a[0] == "support_outing":
            diff += 1
        elif a[0] == "support_rest":
            diff -= 1
        table = _P_OUT_FATIGUE if s[0] == FATIGUE else _P_OUT_STEADY
        return table[diff]

    def transition(self, s, a):
        cond, stage = s
        p = self._pressure(s, a)
        out_obs = ("outing",) * 4
        rest_obs = ("resting",) * 4
        if a[0] == "check":
            return {
                ((cond, OUTING), out_obs): Q_SETTLE * p,
                ((cond, RESTING), rest_obs): Q_SETTLE * (1.0 - p),
                (
                    (cond, ASSESSED),
                    (cond, "assessment", "assessment", "assessment"),
                ): 1.0 - Q_SETTLE,
            }
        return {
            ((cond, OUTING), out_obs): p,
            ((cond, RESTING), rest_obs): 1.0 - p,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
