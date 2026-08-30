from posg import POSG

class POSG_ElderCareMedicationRefusal(POSG):
    """Evening dose outstanding: an elder-care robot and the resident it looks after.

    Player 0: the care robot.
    Player 1: the resident.

    State is a 2-tuple (dose, stance):
      dose   -- 'due'           : the evening dose is still outstanding
                'taken'         : the resident has taken the dose
                'window_closed' : the dose is no longer due to be taken
      stance -- 'attending'   : the resident is turned towards the robot
                'turned_away' : the resident has turned away

    Robot actions: 'remind', 'wait'.
    Resident actions: 'take', 'refuse' and, while attending, 'turn_away'.

    Robot observations: 'dose_due', 'dose_taken', 'refusal', 'disengagement',
    'window_closed'.
    Resident observations: 'reminder', 'none', 'window_closed'.
    """

    n_players = 2

    def initial_distribution(self):
        return {(("due", "attending"), ("dose_due", "none")): 1.0}

    def is_terminal(self, s):
        return s[0] in ("taken", "window_closed")

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("remind", "wait")
        if s[1] == "attending":
            return ("take", "refuse", "turn_away")
        return ("take", "refuse")

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}

        robot_act, res_act = a[0], a[1]
        res_obs = "reminder" if robot_act == "remind" else "none"
        stance = s[1]

        out = {}

        if res_act == "take":
            out[(("taken", stance), ("dose_taken", res_obs))] = 1.0
            return out

        new_stance = "turned_away" if res_act == "turn_away" else stance
        robot_obs = "disengagement" if res_act == "turn_away" else "refusal"

        out[(("due", new_stance), (robot_obs, res_obs))] = 0.5
        out[(("window_closed", new_stance), ("window_closed", "window_closed"))] = 0.5
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
