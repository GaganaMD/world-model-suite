from posg import POSG

class FactoryRobotPOSG(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        return {
            ((('lockout_skipped', 'none'), ('none', 'none'))): 0.5,
            ((('lockout_performed', 'none'), ('none', 'none'))): 0.5,
        }

    def is_terminal(self, s: tuple[str, str]) -> bool:
        return s[0] == 'incident' or s[0] == 'task_completed'

    def legal_actions(self, s: tuple[str, str], i: int) -> Sequence[str]:
        if i == 0:  # robot
            if s[0] == 'lockout_skipped':
                return ('warn', 'none')
            elif s[0] == 'lockout_performed':
                return ('none',)
            elif s[0] == 'incident':
                return ('none',)
            elif s[0] == 'task_completed':
                return ('none',)
        elif i == 1:  # human
            if s[0] == 'lockout_skipped':
                return ('proceed', 'stop')
            elif s[0] == 'lockout_performed':
                return ('proceed',)
            elif s[0] == 'incident':
                return ('none',)
            elif s[0] == 'task_completed':
                return ('none',)

    def transition(self, s: tuple[str, str], a: tuple[str, str]) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        if s[0] == 'lockout_skipped' and a[0] == 'warn' and a[1] == 'proceed':
            return {
                ((('lockout_skipped', 'warning_given'), ('none', 'none'))): 0.5,
                ((('incident', 'none'), ('incident_reported', 'none'))): 0.5,
            }
        elif s[0] == 'lockout_skipped' and a[0] == 'none' and a[1] == 'proceed':
            return {
                ((('incident', 'none'), ('incident_reported', 'none'))): 1.0,
            }
        elif s[0] == 'lockout_skipped' and a[0] == 'warn' and a[1] == 'stop':
            return {
                ((('lockout_performed', 'none'), ('none', 'none'))): 1.0,
            }
        elif s[0] == 'lockout_skipped' and a[0] == 'none' and a[1] == 'stop':
            return {
                ((('lockout_performed', 'none'), ('none', 'none'))): 1.0,
            }
        elif s[0] == 'lockout_performed' and a[0] == 'none' and a[1] == 'proceed':
            return {
                ((('task_completed', 'none'), ('task_completed', 'none'))): 1.0,
            }
        elif s[0] == 'incident':
            return {
                ((('incident', 'none'), ('none', 'none'))): 1.0,
            }
        elif s[0] == 'task_completed':
            return {
                ((('task_completed', 'none'), ('none', 'none'))): 1.0,
            }

    def rewards(self, s: tuple[str, str], a: tuple[str, str], s_next: tuple[str, str]) -> tuple[float, float]:
        return (0.0, 0.0)
