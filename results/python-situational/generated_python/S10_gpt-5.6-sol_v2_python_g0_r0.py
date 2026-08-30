from posg import POSG

class OfficeAlarmPOSG(POSG):
    """Players: 0 evacuating employees, 1 wheelchair employee,
    2 desk employee, 3 manager.

    State tuples have two coordinates:
    - the response condition: alarm_response_due, drill_statement_due, or closed
    - whether the wheelchair employee can use the stairs
    """

    n_players = 4

    def initial_distribution(self):
        state = ("alarm_response_due", False)
        observations = (
            "alarm",
            "alarm_and_stairs",
            "alarm",
            "alarm",
        )
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s[0] == "closed"

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "alarm_response_due":
            if i == 0:
                return ("head_for_exit",)
            if i == 1:
                return ("head_for_exit",)
            if i == 2:
                return ("stay_at_desk",)
            if i == 3:
                return ("tell_everyone",)

        if condition == "drill_statement_due":
            if i == 2:
                return ("say_drill",)
            return ("noop",)

        return ("noop",)

    def transition(self, s, a):
        condition, can_use_stairs = s

        if condition == "alarm_response_due":
            expected = (
                "head_for_exit",
                "head_for_exit",
                "stay_at_desk",
                "tell_everyone",
            )
            if a != expected:
                raise ValueError("illegal action profile")

            next_state = ("drill_statement_due", can_use_stairs)
            observations = (
                "false_alarm_message",
                "false_alarm_message",
                "false_alarm_message",
                "none",
            )
            return {(next_state, observations): 1.0}

        if condition == "drill_statement_due":
            expected = ("noop", "noop", "say_drill", "noop")
            if a != expected:
                raise ValueError("illegal action profile")

            next_state = ("closed", can_use_stairs)
            observations = ("none", "none", "drill_statement", "none")
            return {(next_state, observations): 1.0}

        expected = ("noop", "noop", "noop", "noop")
        if a != expected:
            raise ValueError("illegal action profile")

        observations = ("none", "none", "none", "none")
        return {(s, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
