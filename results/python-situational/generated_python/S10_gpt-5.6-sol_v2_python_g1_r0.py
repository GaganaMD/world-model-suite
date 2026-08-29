from posg import POSG

class OfficeAlarmPOSG(POSG):
    """Players: 0 assistant robot; 1 employees acting collectively; 2 wheelchair
    employee; 3 employee who stays and speaks; 4 manager.

    State tuple: (interaction condition, wheelchair employee's stair-use condition).
    """

    n_players = 5

    def initial_distribution(self):
        state = ("alarm_sounding", "stairs_unavailable")
        observations = ("alarm", "alarm", "alarm", "alarm", "alarm")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s[0] == "claims_spoken"

    def legal_actions(self, s, i):
        if not 0 <= i < self.n_players:
            raise IndexError("player index out of range")

        condition = s[0]

        if condition == "alarm_sounding":
            actions = (
                ("noop",),
                ("head_for_exit",),
                ("noop",),
                ("stay",),
                ("tell_everyone",),
            )
            return actions[i]

        if condition == "instruction_heard":
            return ("say_probably_drill",) if i == 3 else ("noop",)

        if condition == "claims_spoken":
            return ("noop",)

        raise ValueError("unknown state")

    def transition(self, s, a):
        condition, stair_condition = s

        if condition == "alarm_sounding":
            expected = (
                "noop",
                "head_for_exit",
                "noop",
                "stay",
                "tell_everyone",
            )
            if a != expected:
                raise ValueError("illegal action profile")

            next_state = ("instruction_heard", stair_condition)
            observations = (
                "false_alarm_keep_working",
                "false_alarm_keep_working",
                "false_alarm_keep_working",
                "false_alarm_keep_working",
                "none",
            )
            return {(next_state, observations): 1.0}

        if condition == "instruction_heard":
            expected = ("noop", "noop", "noop", "say_probably_drill", "noop")
            if a != expected:
                raise ValueError("illegal action profile")

            next_state = ("claims_spoken", stair_condition)
            observations = (
                "drill_claim",
                "drill_claim",
                "drill_claim",
                "drill_claim",
                "drill_claim",
            )
            return {(next_state, observations): 1.0}

        if condition == "claims_spoken":
            expected = ("noop", "noop", "noop", "noop", "noop")
            if a != expected:
                raise ValueError("illegal action profile")
            observations = ("none", "none", "none", "none", "none")
            return {(s, observations): 1.0}

        raise ValueError("unknown state")

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
