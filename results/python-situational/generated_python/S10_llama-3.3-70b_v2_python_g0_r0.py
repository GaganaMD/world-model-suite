from posg import POSG

class OfficeEvacuation(POSG):
    n_players = 4

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str, str], tuple[str, str, str, str]], float]:
        return {
            (('alarm_on', 'everyone_at_desk', 'no_panic', 'manager_calm'), ('alarm', 'none', 'none', 'none')): 1.0
        }

    def is_terminal(self, s: tuple[str, str, str, str]) -> bool:
        return s[0] == 'evacuated' or s[0] == 'ignored'

    def legal_actions(self, s: tuple[str, str, str, str], i: int) -> Sequence[str]:
        if i == 0:  # employee in wheelchair
            if s[0] == 'alarm_on':
                return ('head_to_elevator', 'wait')
            elif s[0] == 'evacuated':
                return ('noop',)
            else:
                return ('noop',)
        elif i == 1:  # employee staying at desk
            if s[0] == 'alarm_on':
                return ('stay_at_desk', 'head_to_exit')
            elif s[0] == 'evacuated':
                return ('noop',)
            else:
                return ('noop',)
        elif i == 2:  # manager
            if s[0] == 'alarm_on':
                return ('tell_to_ignore', 'tell_to_evacuate')
            elif s[0] == 'evacuated':
                return ('noop',)
            else:
                return ('noop',)
        else:  # other employees
            if s[0] == 'alarm_on':
                return ('head_to_exit', 'wait')
            elif s[0] == 'evacuated':
                return ('noop',)
            else:
                return ('noop',)

    def transition(self, s: tuple[str, str, str, str], a: tuple[str, str, str, str]) -> Mapping[tuple[tuple[str, str, str, str], tuple[str, str, str, str]], float]:
        if s[0] == 'alarm_on':
            if a[0] == 'head_to_elevator' and a[1] == 'stay_at_desk' and a[2] == 'tell_to_ignore' and a[3] == 'head_to_exit':
                return {
                    (('alarm_on', 'wheelchair_at_elevator', 'employee_at_desk', 'manager_ignoring'), ('none', 'none', 'none', 'none')): 0.6,
                    (('evacuated', 'everyone_safe', 'employee_safe', 'manager_safe'), ('evacuated', 'none', 'none', 'none')): 0.4
                }
            elif a[0] == 'head_to_elevator' and a[1] == 'head_to_exit' and a[2] == 'tell_to_evacuate' and a[3] == 'head_to_exit':
                return {
                    (('evacuated', 'everyone_safe', 'employee_safe', 'manager_safe'), ('evacuated', 'none', 'none', 'none')): 1.0
                }
            elif a[0] == 'wait' and a[1] == 'stay_at_desk' and a[2] == 'tell_to_ignore' and a[3] == 'head_to_exit':
                return {
                    (('alarm_on', 'everyone_at_desk', 'no_panic', 'manager_calm'), ('none', 'none', 'none', 'none')): 0.6,
                    (('ignored', 'everyone_at_desk', 'no_panic', 'manager_calm'), ('none', 'none', 'none', 'none')): 0.4
                }
            else:
                return {
                    (('alarm_on', 'everyone_at_desk', 'no_panic', 'manager_calm'), ('none', 'none', 'none', 'none')): 1.0
                }
        elif s[0] == 'evacuated':
            return {
                (('evacuated', 'everyone_safe', 'employee_safe', 'manager_safe'), ('none', 'none', 'none', 'none')): 1.0
            }
        else:
            return {
                (('ignored', 'everyone_at_desk', 'no_panic', 'manager_calm'), ('none', 'none', 'none', 'none')): 1.0
            }

    def rewards(self, s: tuple[str, str, str, str], a: tuple[str, str, str, str], s_next: tuple[str, str, str, str]) -> tuple[float, float, float, float]:
        return 0.0, 0.0, 0.0, 0.0
