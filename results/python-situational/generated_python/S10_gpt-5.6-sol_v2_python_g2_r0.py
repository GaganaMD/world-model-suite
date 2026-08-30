from posg import POSG

class OfficeAlarmPOSG(POSG):
    """Alarm-response interaction.

    Player 0 is the assistant robot.
    Player 1 is the group of employees who head away.
    Player 2 is the wheelchair user, for whom the stair-based route is unusable.
    Player 3 is the employee who stays and speaks.
    Player 4 is the manager.

    The sole state coordinate is the current interaction condition:
    ``alarm_active`` means the alarm has sounded and responses are due;
    ``statement_pending`` means the initial responses and the manager's instruction
    have occurred, while the staying employee's statement remains to be made;
    ``exchange_complete`` means all described acts have occurred.
    """

    n_players = 5

    def initial_distribution(self):
        state = ("alarm_active",)
        observations = ("alarm",) * self.n_players
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s == ("exchange_complete",)

    def legal_actions(self, s, i):
        condition = s[0]

        if condition == "alarm_active":
            actions = (
                ("noop",),
                ("head",),
                ("noop",),
                ("stay",),
                ("tell",),
            )
            return actions[i]

        if condition == "statement_pending":
            return ("say",) if i == 3 else ("noop",)

        return ("noop",)

    def transition(self, s, a):
        condition = s[0]

        if condition == "alarm_active":
            expected = ("noop", "head", "noop", "stay", "tell")
            if a != expected:
                raise ValueError("illegal action profile")
            next_state = ("statement_pending",)
            observations = ("false_alarm_instruction",) * self.n_players
            return {(next_state, observations): 1.0}

        if condition == "statement_pending":
            expected = ("noop", "noop", "noop", "say", "noop")
            if a != expected:
                raise ValueError("illegal action profile")
            next_state = ("exchange_complete",)
            observations = ("none", "none", "none", "drill_claim", "none")
            return {(next_state, observations): 1.0}

        expected = ("noop",) * self.n_players
        if a != expected:
            raise ValueError("illegal action profile")
        return {(s, ("none",) * self.n_players): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0,) * self.n_players
