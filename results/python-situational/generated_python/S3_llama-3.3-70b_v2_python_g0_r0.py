from posg import POSG

class AirportPickup(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {((True, True), ('man_boarded', 'none')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return not s[0] or not s[1]

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if i == 0:
            if s[0] and s[1]:
                return ('drive_away', 'pick_up_woman')
            elif s[0] and not s[1]:
                return ('drive_away',)
            elif not s[0] and s[1]:
                return ('pick_up_woman', 'noop')
            else:
                return ('noop',)
        else:
            if s[0] and s[1]:
                return ('get_in', 'ask_driver_to_pick_up_woman')
            elif s[0] and not s[1]:
                return ('get_in', 'noop')
            elif not s[0] and s[1]:
                return ('ask_driver_to_pick_up_woman', 'noop')
            else:
                return ('noop',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if a[0] == 'drive_away':
            return {((False, True), ('none', 'car_left')): 1.0}
        elif a[0] == 'pick_up_woman':
            return {((True, False), ('woman_picked_up', 'picked_up')): 1.0}
        elif a[1] == 'get_in':
            return {((True, True), ('none', 'none')): 1.0}
        elif a[1] == 'ask_driver_to_pick_up_woman':
            return {((True, True), ('none', 'asked')): 1.0}
        else:
            return {(s, ('none', 'none')): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float,...]:
        return (0.0, 0.0)
