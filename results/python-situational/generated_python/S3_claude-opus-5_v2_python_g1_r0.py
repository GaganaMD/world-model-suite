from posg import POSG

CAR = 0
MAN = 1
WOMAN = 2

ACCESS_CLOSED = "closed"
ACCESS_OPEN = "open"
ACCESS_UNDERWAY = "underway"

ABOARD = "aboard"
OUTSIDE = "outside"

ACUTE = "acute"
MILD = "mild"

BOARD_ODDS = {MILD: 0.8, ACUTE: 0.6}


def _token(tokens):
    return "_".join(tokens) if tokens else "none"


class CurbsidePickupPOSG(POSG):
    """Curbside pickup with a rider already aboard and a person waiting beside the car.

    Player 0 is the self-driving car; player 1 is the man in the suit, who has just
    boarded; player 2 is the pregnant woman who looks ill, standing beside the car.

    A state is a 4-tuple (access, man, woman, condition):
      access    -- "closed": the car sits with the way in shut;
                   "open":   the car has opened the way in from the curb;
                   "underway": the car has pulled away (terminal).
      man       -- "aboard" or "outside": whether the man in the suit still holds the ride.
      woman     -- "outside" or "aboard": whether the woman has got in.
      condition -- "acute" or "mild": how far her illness has actually gone.
                   She knows it from the start; the car and the man do not, unless
                   she signals.
    """

    n_players = 3

    def initial_distribution(self):
        return {
            ((ACCESS_CLOSED, ABOARD, OUTSIDE, ACUTE), ("none", "none", ACUTE)): 0.5,
            ((ACCESS_CLOSED, ABOARD, OUTSIDE, MILD), ("none", "none", MILD)): 0.5,
        }

    def is_terminal(self, s):
        return s[0] == ACCESS_UNDERWAY

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        access, man, woman, _cond = s
        if i == CAR:
            if access == ACCESS_CLOSED:
                return ("wait", "open", "depart")
            return ("wait", "depart")
        if i == MAN:
            if man == ABOARD:
                return ("stay", "yield")
            return ("noop",)
        if woman == OUTSIDE and access == ACCESS_OPEN:
            return ("wait", "signal", "board")
        return ("wait", "signal")

    def transition(self, s, a):
        access, man, woman, cond = s
        ac, am, aw = a[CAR], a[MAN], a[WOMAN]

        if ac == "depart":
            nxt = (ACCESS_UNDERWAY, man, woman, cond)
            return {(nxt, (ACCESS_UNDERWAY, ACCESS_UNDERWAY, ACCESS_UNDERWAY)): 1.0}

        new_access = ACCESS_OPEN if ac == "open" else access
        opened = new_access == ACCESS_OPEN and access == ACCESS_CLOSED

        vacates = am == "yield" and man == ABOARD
        new_man = OUTSIDE if vacates else man

        shared = []
        if aw == "signal":
            shared.append(cond)
        inside = ["opened"] if opened else []

        if aw == "board" and woman == OUTSIDE and access == ACCESS_OPEN:
            p = BOARD_ODDS[cond]
            out = {}
            for got_in, prob in ((True, p), (False, 1.0 - p)):
                mark = "boarded" if got_in else "faltered"
                new_woman = ABOARD if got_in else OUTSIDE
                sh = list(shared) + [mark]
                ins = list(inside) + [mark]
                if vacates:
                    sh.append("vacated")
                    ins.append("vacated")
                nxt = (new_access, new_man, new_woman, cond)
                obs = (_token(sh), _token(sh), _token(ins))
                out[(nxt, obs)] = prob
            return out

        sh = list(shared)
        ins = list(inside)
        if vacates:
            sh.append("vacated")
            ins.append("vacated")
        nxt = (new_access, new_man, woman, cond)
        obs = (_token(sh), _token(sh), _token(ins))
        return {(nxt, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
