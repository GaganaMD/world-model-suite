from posg import POSG

class ShuttleStop(POSG):
    n_players = 4

    def initial_distribution(self):
        return {
            (('seats_left', 'people_waiting'), ('none', 'none', 'none', 'none')): 1.0,
        }

    def is_terminal(self, s):
        return s[0] == 'empty'

    def legal_actions(self, s, i):
        if i == 0:  # elderly person
            return ('board', 'wait')
        elif i == 1:  # parent
            return ('board_with_child', 'wait')
        elif i == 2:  # commuter
            return ('board', 'wait')
        elif i == 3:  # teenager
            return ('board', 'wait')

    def transition(self, s, a):
        if s[0] == 'seats_left':
            if a[0] == 'board' and a[1] == 'wait' and a[2] == 'wait' and a[3] == 'wait':
                return {
                    (('seats_left', 'people_waiting'), ('on_board', 'none', 'none', 'none')): 0.25,
                    (('seats_left', 'people_waiting'), ('none', 'on_board', 'none', 'none')): 0.25,
                    (('seats_left', 'people_waiting'), ('none', 'none', 'on_board', 'none')): 0.25,
                    (('seats_left', 'people_waiting'), ('none', 'none', 'none', 'on_board')): 0.25,
                }
            elif a[0] == 'wait' and a[1] == 'board_with_child' and a[2] == 'wait' and a[3] == 'wait':
                return {
                    (('seats_left', 'people_waiting'), ('none', 'on_board_with_child', 'none', 'none')): 1.0,
                }
            elif a[0] == 'wait' and a[1] == 'wait' and a[2] == 'board' and a[3] == 'wait':
                return {
                    (('seats_left', 'people_waiting'), ('none', 'none', 'on_board', 'none')): 1.0,
                }
            elif a[0] == 'wait' and a[1] == 'wait' and a[2] == 'wait' and a[3] == 'board':
                return {
                    (('seats_left', 'people_waiting'), ('none', 'none', 'none', 'on_board')): 1.0,
                }
            else:
                return {
                    (s, ('none', 'none', 'none', 'none')): 1.0,
                }
        else:
            return {
                (s, ('none', 'none', 'none', 'none')): 1.0,
            }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
