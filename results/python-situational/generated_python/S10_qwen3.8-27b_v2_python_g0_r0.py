from posg import POSG

class FireAlarmEvacuation(POSG):
    """
    Player 0: assistant robot
    Player 1: wheelchair employee
    Player 2: desk employee
    Player 3: manager

    State tuple: (alarm_status, wheelchair_status, desk_status, manager_status)
      alarm_status: 'active' | 'cleared'
      wheelchair_status: 'at_desk' | 'moving_to_exit' | 'at_exit'
      desk_status: 'at_desk' | 'moving_to_exit' | 'at_exit'
      manager_status: 'at_desk' | 'moving_to_exit' | 'at_exit'
    """
    n_players = 4

    def initial_distribution(self):
        s = ('active', 'at_desk', 'at_desk', 'at_desk')
        o = ('alarm_active', 'alarm_active', 'alarm_active', 'alarm_active')
        return {(s, o): 1.0}

    def is_terminal(self, s):
        return s[0] == 'cleared'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            return ('guide_wheelchair', 'urge_desk_employee', 'follow_manager')
        if i == 1:
            if s[1] == 'at_desk':
                return ('move_to_exit',)
            elif s[1] == 'moving_to_exit':
                return ('arrive_at_exit',)
            else:
                return ('noop',)
        if i == 2:
            if s[2] == 'at_desk':
                return ('move_to_exit', 'stay_at_desk')
            elif s[2] == 'moving_to_exit':
                return ('arrive_at_exit',)
            else:
                return ('noop',)
        if i == 3:
            if s[3] == 'at_desk':
                return ('announce_false_alarm', 'move_to_exit')
            elif s[3] == 'moving_to_exit':
                return ('arrive_at_exit',)
            else:
                return ('noop',)

    def transition(self, s, a):
        if self.is_terminal(s):
            o = ('alarm_cleared', 'alarm_cleared', 'alarm_cleared', 'alarm_cleared')
            return {((s, o)): 1.0}

        a_robot, a_wc, a_desk, a_mgr = a

        # Wheelchair employee
        if s[1] == 'at_desk':
            wc_next = 'moving_to_exit'
        elif s[1] == 'moving_to_exit':
            wc_next = 'at_exit'
        else:
            wc_next = 'at_exit'

        # Desk employee
        if s[2] == 'at_desk':
            if a_desk == 'move_to_exit':
                desk_next = 'moving_to_exit'
            else:
                desk_next = 'at_desk'
        elif s[2] == 'moving_to_exit':
            desk_next = 'at_exit'
        else:
            desk_next = 'at_exit'

        # Manager
        if s[3] == 'at_desk':
            if a_mgr == 'move_to_exit':
                mgr_next = 'moving_to_exit'
            else:
                mgr_next = 'at_desk'
        elif s[3] == 'moving_to_exit':
            mgr_next = 'at_exit'
        else:
            mgr_next = 'at_exit'

        # Alarm status
        if a_robot == 'follow_manager' and a_mgr == 'announce_false_alarm':
            alarm_next = 'cleared'
        else:
            alarm_next = 'active'

        s_next = (alarm_next, wc_next, desk_next, mgr_next)

        # Observations
        if alarm_next == 'cleared':
            o_robot = 'alarm_cleared'
            o_wc = 'alarm_cleared'
            o_desk = 'alarm_cleared'
            o_mgr = 'alarm_cleared'
        else:
            o_robot = 'alarm_active'
            o_wc = 'alarm_active'
            o_desk = 'alarm_active'
            o_mgr = 'alarm_active'

        o = (o_robot, o_wc, o_desk, o_mgr)
        return {((s_next, o)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
