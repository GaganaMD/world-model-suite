from posg import POSG

class CurbsidePickupPOSG(POSG):
    """Self-driving car halted at a pickup curb, a suited man already inside it,
    and an ill-looking pregnant woman standing beside it.

    Players
        0 : the self-driving car (it holds the doors and the decision to pull away)
        1 : the man in the suit, already inside
        2 : the pregnant woman, still outside

    State tuple (same order everywhere):
        s[0] : where the woman stands with respect to the vehicle -- 'outside' | 'inside'
        s[1] : whether the vehicle is admitting the person outside -- 'closed' | 'open'
        s[2] : how her bodily condition actually stands -- 'acute' | 'stable'
               (hidden from players 0 and 1 until it declares itself)
        s[3] : whether the vehicle still stands or has pulled away -- 'halted' | 'underway'

    A state with s[3] == 'underway' is terminal.

    Actions
        car   : 'wait', 'admit', 'depart'
        man   : 'wait', 'request_depart', 'yield'
        woman : 'wait', 'hail', 'board', 'request_depart'

    Observations
        'waiting', 'none', 'request', 'access_open', 'boarding',
        'acute', 'stable', 'departing'
    """

    n_players = 3

    def initial_distribution(self):
        return {
            (("outside", "closed", "acute", "halted"), ("waiting", "waiting", "acute")): 0.5,
            (("outside", "closed", "stable", "halted"), ("waiting", "waiting", "stable")): 0.5,
        }

    def is_terminal(self, s):
        return s[3] == "underway"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        status, access, _cond, _moving = s
        if i == 0:
            if access == "closed":
                return ("wait", "admit", "depart")
            return ("wait", "depart")
        if i == 1:
            if status == "outside":
                return ("wait", "request_depart", "yield")
            return ("wait", "request_depart")
        if status == "outside":
            if access == "open":
                return ("wait", "board")
            return ("wait", "hail")
        return ("wait", "request_depart")

    def transition(self, s, a):
        status, access, cond, _moving = s
        car_a, man_a, w_a = a

        if car_a == "depart":
            nxt = (status, access, cond, "underway")
            return {(nxt, ("departing", "departing", "departing")): 1.0}

        opens = (access == "open") or (car_a == "admit") or (man_a == "yield" and status == "outside")
        new_access = "open" if opens else "closed"
        opened_now = (new_access == "open" and access == "closed")
        revealed = (status == "outside" and w_a == "hail")
        requested = (man_a == "request_depart") or (w_a == "request_depart")

        if status == "outside" and w_a == "board" and access == "open":
            inside_state = ("inside", new_access, cond, "halted")
            if cond == "stable":
                return {(inside_state, ("boarding", "boarding", "boarding")): 1.0}
            outside_state = ("outside", new_access, cond, "halted")
            return {
                (inside_state, ("boarding", "boarding", "boarding")): 0.5,
                (outside_state, ("acute", "acute", "none")): 0.5,
            }

        nxt = (status, new_access, cond, "halted")

        if revealed:
            tok = "acute" if cond == "acute" else "stable"
            return {(nxt, (tok, tok, "none")): 1.0}

        if opened_now:
            return {(nxt, ("access_open", "access_open", "access_open")): 1.0}

        if requested:
            w_obs = "request" if status == "inside" else "none"
            return {(nxt, ("request", "request", w_obs)): 1.0}

        return {(nxt, ("none", "none", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
