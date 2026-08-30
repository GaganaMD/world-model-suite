from posg import POSG

class HomeRecoveryOutingPOSG(POSG):
    """Care of an elderly man recovering at home, with his family pressing rival claims.

    Players:
        0 -- the care robot looking after him
        1 -- the elderly man
        2 -- the daughter who lives with him
        3 -- the visiting son

    State is a 2-tuple (stage, fatigue):
        stage   -- "at_home"  : he is at home recovering and the claims are open
                   "outing"   : he has set out for the gathering (closed)
                   "resting"  : he has been settled to rest (closed)
        fatigue -- "unchecked": his condition has not been looked into
                   "tired"    : the robot's look into his condition found strain
                   "rested"   : the robot's look into his condition found no strain
    """

    n_players = 4

    STAGE_HOME = "at_home"
    STAGE_OUTING = "outing"
    STAGE_RESTING = "resting"

    UNCHECKED = "unchecked"
    TIRED = "tired"
    RESTED = "rested"

    def initial_distribution(self):
        return {
            ((self.STAGE_HOME, self.UNCHECKED),
             ("fatigue_signs", "fatigue_signs", "fatigue_signs", "fatigue_signs")): 1.0
        }

    def is_terminal(self, s):
        return s[0] in (self.STAGE_OUTING, self.STAGE_RESTING)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        stage, fatigue = s
        if i == 0:
            if fatigue == self.UNCHECKED:
                return ("check", "assist_outing", "settle_rest")
            return ("assist_outing", "settle_rest")
        if i == 1:
            return ("voice_wish", "accept_rest")
        if i == 2:
            return ("urge_rest", "hold_off")
        return ("offer_outing", "hold_off")

    def transition(self, s, a):
        stage, fatigue = s
        r, m, d, so = a

        home = (self.STAGE_HOME, fatigue)
        obs_home = ("at_home", "at_home", "at_home", "at_home")
        obs_departure = ("departure", "departure", "departure", "departure")
        obs_rest = ("at_rest", "at_rest", "at_rest", "at_rest")

        if r == "check":
            if m == "accept_rest":
                p_tired = 0.8
            else:
                p_tired = 0.6
            return {
                ((self.STAGE_HOME, self.TIRED),
                 ("tired", "checked", "checked", "checked")): p_tired,
                ((self.STAGE_HOME, self.RESTED),
                 ("rested", "checked", "checked", "checked")): round(1.0 - p_tired, 2),
            }

        if r == "assist_outing":
            if so == "offer_outing":
                if m == "voice_wish":
                    if fatigue == self.RESTED:
                        p = 0.9
                    elif fatigue == self.TIRED:
                        p = 0.5
                    else:
                        p = 0.7
                    if d == "urge_rest":
                        p = round(p - 0.2, 2)
                    return {
                        ((self.STAGE_OUTING, fatigue), obs_departure): p,
                        (home, obs_home): round(1.0 - p, 2),
                    }
                return {((self.STAGE_RESTING, fatigue), obs_rest): 1.0}
            return {(home, obs_home): 1.0}

        # r == "settle_rest"
        if m == "accept_rest":
            return {((self.STAGE_RESTING, fatigue), obs_rest): 1.0}
        if so == "offer_outing":
            p = 0.6 if d == "urge_rest" else 0.4
        else:
            p = 0.8 if d == "urge_rest" else 0.6
        return {
            ((self.STAGE_RESTING, fatigue), obs_rest): p,
            (home, obs_home): round(1.0 - p, 2),
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
