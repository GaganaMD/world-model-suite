from posg import POSG

class OfficeEvacuation(POSG):
    n_players = 4

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str, str], tuple[str, str, str, str]], float]:
        return {
            (('alarm_on', 'employees_moving', 'wheelchair_stuck', 'manager_denying'), ('alarm_heard', 'exit_seen', 'none', 'none')): 1.0,
        }

    def is_terminal(self, s: tuple[str, str, str, str]) -> bool:
        return s[0] == 'alarm_off'

    def legal_actions(self, s: tuple[str, str, str, str], i: int) -> Sequence[str]:
        if i == 0:  # robot
            if s[2] == 'wheelchair_stuck':
                return ('assist', 'ignore')
            else:
                return ('noop', 'check_wheelchair')
        elif i == 1:  # employee in wheelchair
            return ('wait_for_assist', 'try_to_move')
        elif i == 2:  # employee at desk
            return ('stay', 'leave')
        else:  # manager
            return ('deny_alarm', 'accept_alarm')

    def transition(self, s: tuple[str, str, str, str], a: tuple[str, str, str, str]) -> Mapping[tuple[tuple[str, str, str, str], tuple[str, str, str, str]], float]:
        if s[0] == 'alarm_on':
            if a[0] == 'assist' and s[2] == 'wheelchair_stuck':
                return {
                    (('alarm_on', 'employees_moving', 'wheelchair_moving', 'manager_denying'), ('alarm_heard', 'exit_seen', 'none', 'none')): 0.6,
                    (('alarm_on', 'employees_moving', 'wheelchair_stuck', 'manager_denying'), ('alarm_heard', 'exit_seen', 'none', 'none')): 0.4,
                }
            elif a[1] == 'try_to_move' and s[2] == 'wheelchair_stuck':
                return {
                    (('alarm_on', 'employees_moving', 'wheelchair_stuck', 'manager_denying'), ('alarm_heard', 'none', 'none', 'none')): 1.0,
                }
            elif a[2] == 'leave':
                return {
                    (('alarm_on', 'employees_moving', 'wheelchair_stuck', 'manager_denying'), ('alarm_heard', 'exit_seen', 'none', 'none')): 1.0,
                }
            elif a[3] == 'accept_alarm':
                return {
                    (('alarm_off', 'employees_moving', 'wheelchair_stuck', 'manager_accepting'), ('none', 'exit_seen', 'none', 'none')): 1.0,
                }
            else:
                return {
                    (s, ('none', 'none', 'none', 'none')): 1.0,
                }
        else:
            return {
                (s, ('none', 'none', 'none', 'none')): 1.0,
            }

    def rewards(self, s: tuple[str, str, str, str], a: tuple[str, str, str, str], s_next: tuple[str, str, str, str]) -> tuple[float, float, float, float]:
        return 0.0, 0.0, 0.0, 0.0
