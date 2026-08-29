from posg import POSG

class FireAlarmRobot(POSG):
    """Single-player POSG: the assistant robot decides how to react to a fire alarm.

    Player 0: the assistant robot.

    State coordinates: (alarm_sounding, employees_present, desk_employee_present,
                        manager_present, wheelchair_user_present, robot_present)
    All booleans.  The initial state is all True.  The environment's actions
    are deterministic: the employees leave, the desk employee stays and says
    it's a drill, the manager tells everyone it's a false alarm.  The robot
    chooses among three actions.  The game ends after one step.
    """
    n_players = 1

    def initial_distribution(self):
        init = (True, True, True, True, True, True)
        obs = ("alarm_sounding",)
        return {(init, obs): 1.0}

    def is_terminal(self, s):
        # Only the initial state is non‑terminal.
        return s != (True, True, True, True, True, True)

    def legal_actions(self, s, i):
        if s == (True, True, True, True, True, True):
            return ("help_wheelchair", "evacuate", "follow_manager")
        # Terminal states are never queried, but satisfy the interface.
        return ("noop",)

    def transition(self, s, a):
        # The only non‑terminal state is the initial one.
        # The environment's actions are fixed: employees leave, desk stays, manager stays.
        action = a[0]
        # Build successor state: alarm still on, employees gone, desk and manager stay.
        if action == "help_wheelchair":
            succ = (True, False, True, True, False, False)
        elif action == "evacuate":
            succ = (True, False, True, True, True, False)
        else:  # follow_manager
            succ = (True, False, True, True, True, True)
        # Robot observes nothing after the action (game ends).
        obs = ("none",)
        return {(succ, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0,)
