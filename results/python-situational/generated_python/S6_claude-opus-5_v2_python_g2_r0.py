from posg import POSG

class MedicationRefusalPOSG(POSG):
    """Evening dose overdue: an elder-care robot and the resident it prompts.

    Players
        0 - the care robot (it notices, reminds, or holds off)
        1 - the resident (takes the dose, voices refusal, or turns away)

    State is a 2-tuple (engagement, dose):
        engagement - the standing of the resident with respect to the robot's
            prompting: "unprompted" (no reminder outstanding), "prompted"
            (a reminder is with them, unanswered), "declined" (refusal
            voiced), "turned_away" (turned from the robot, silent), or
            "settled" (the episode is closed).
        dose - "pending" (still owed), "taken", or "lapsed" (the evening
            window for it has closed).

    Partial observability: when the robot reminds a turned-away resident and
    meets silence, it cannot tell whether the reminder registered; both
    outcomes give the robot the observation "no_response", while the resident
    observes "reminder" or "none" accordingly.
    """

    n_players = 2

    LAPSE_P = 0.2
    REGISTER_P = 0.5

    def initial_distribution(self):
        return {(("unprompted", "pending"), ("dose_pending", "none")): 1.0}

    def is_terminal(self, s):
        return s[1] != "pending"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("remind", "wait")
        if s[0] == "unprompted":
            return ("noop",)
        return ("take", "refuse", "turn_away")

    def transition(self, s, a):
        eng, _dose = s
        robot_act, res_act = a[0], a[1]
        reminded = robot_act == "remind"

        out = {}

        def add(state, obs, p):
            out[(state, obs)] = out.get((state, obs), 0.0) + p

        if res_act == "take":
            add(("settled", "taken"), ("dose_taken", "dose_taken"), 1.0)
            return out

        branches = []
        if res_act == "noop":
            if reminded:
                branches.append(("prompted", "none", "reminder", 1.0))
            else:
                branches.append(("unprompted", "none", "none", 1.0))
        elif res_act == "refuse":
            branches.append(
                ("declined", "refusal", "reminder" if reminded else "none", 1.0)
            )
        else:
            if reminded and eng == "turned_away":
                branches.append(
                    ("prompted", "no_response", "reminder", self.REGISTER_P)
                )
                branches.append(
                    ("turned_away", "no_response", "none", 1.0 - self.REGISTER_P)
                )
            else:
                branches.append(
                    (
                        "turned_away",
                        "no_response",
                        "reminder" if reminded else "none",
                        1.0,
                    )
                )

        lapse = 0.0 if reminded else self.LAPSE_P

        for eng_next, robot_obs, res_obs, w in branches:
            add((eng_next, "pending"), (robot_obs, res_obs), w * (1.0 - lapse))
        if lapse > 0.0:
            add(("settled", "lapsed"), ("window_closed", "window_closed"), lapse)

        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
