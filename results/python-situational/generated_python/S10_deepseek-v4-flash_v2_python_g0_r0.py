from posg import POSG

class FireAlarmPOSG(POSG):
    """
    Players:
        0: Robot
        1: Wheelchair employee
        2: Desk employee
        3: Manager

    State: a tuple (alarm_type,). alarm_type is 0 for drill, 1 for real fire
    in non-terminal states; in terminal states it is a string describing the outcome.

    Actions:
        Robot: assist, leave, wait
        Wheelchair: call, stay
        Desk: stay, leave
        Manager: noop

    Observations:
        Initial: all observe "alarm_announce"
        Terminal: all observe "end"
    """
    n_players = 4

    def initial_distribution(self):
        obs = ("alarm_announce",) * 4
        return {((0,), obs): 0.5, ((1,), obs): 0.5}

    def is_terminal(self, s):
        return isinstance(s[0], str)

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ()
        if i == 0:          # Robot
            return ("assist", "leave", "wait")
        elif i == 1:        # Wheelchair
            return ("call", "stay")
        elif i == 2:        # Desk
            return ("stay", "leave")
        elif i == 3:        # Manager
            return ("noop",)

    def transition(self, s, a):
        alarm = s[0]
        if alarm == 0:      # drill
            next_state = ("drill",)
        else:               # real fire
            a_robot, a_wheel, a_desk, _ = a
            help_ = (a_robot == "assist" and a_wheel == "call")
            desk_left = (a_desk == "leave")
            if help_ and desk_left:
                next_state = ("real_helped_desk_left",)
            elif help_ and not desk_left:
                next_state = ("real_helped_desk_stayed",)
            elif not help_ and desk_left:
                next_state = ("real_not_helped_desk_left",)
            else:
                next_state = ("real_not_helped_desk_stayed",)
        obs = ("end",) * 4
        return {(next_state, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0,) * 4
