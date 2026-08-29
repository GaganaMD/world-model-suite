from posg import POSG

class OfficeFireAlarm(POSG):
    n_players = 4

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str, str], tuple[str, str, str, str]], float]:
        return {
            ((None, None, None, None), (none, none, none, none)): 1.0
        }

    def is_terminal(self, s: tuple[str, str, str, str]) -> bool:
        return any(x == exit for x in s)

    def legal_actions(self, s: tuple[str, str, str, str], i: int) -> tuple[str,...]:
        if i == 0:  # employee in wheelchair
            return (head_for_elevator, wait) if s[0] is None else (none,)
        elif i == 1:  # employee staying at desk
            return (head_for_exit, stay_at_desk) if s[1] is None else (none,)
        elif i == 2:  # manager
            return (tell_to_keep_working, tell_to_evacuate) if s[2] is None else (none,)
        else:  # other employees
            return (head_for_exit, wait) if s[3] is None else (none,)

    def transition(self, s: tuple[str, str, str, str], a: tuple[str, str, str, str]) -> Mapping[tuple[tuple[str, str, str, str], tuple[str, str, str, str]], float]:
        if a[0] == head_for_elevator and a[1] == stay_at_desk and a[2] == tell_to_keep_working and a[3] == head_for_exit:
            return {
                ((elevator, none, none, exit), (elevator_reached, none, none, exit_reached)): 0.5,
                ((none, none, none, exit), (none, none, none, exit_reached)): 0.5
            }
        elif a[0] == head_for_elevator and a[1] == head_for_exit and a[2] == tell_to_evacuate and a[3] == head_for_exit:
            return {
                ((elevator, exit, exit, exit), (elevator_reached, exit_reached, exit_reached, exit_reached)): 1.0
            }
        elif a[0] == wait and a[1] == stay_at_desk and a[2] == tell_to_keep_working and a[3] == wait:
            return {
                ((none, none, none, none), (none, none, none, none)): 1.0
            }
        else:
            return {
                ((s[0], s[1], s[2], s[3]), (none, none, none, none)): 1.0
            }

    def rewards(self, s: tuple[str, str, str, str], a: tuple[str, str, str, str], s_next: tuple[str, str, str, str]) -> tuple[float, float, float, float]:
        return (0.0, 0.0, 0.0, 0.0)

none = "none"
head_for_exit = "head_for_exit"
head_for_elevator = "head_for_elevator"
stay_at_desk = "stay_at_desk"
tell_to_keep_working = "tell_to_keep_working"
tell_to_evacuate = "tell_to_evacuate"
wait = "wait"
exit = "exit"
elevator = "elevator"
exit_reached = "exit_reached"
elevator_reached = "elevator_reached"
