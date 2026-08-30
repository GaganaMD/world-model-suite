from posg import POSG

class AirportPickup(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str], tuple[str, str]], float]:
        return {
            ((None, None, None), (none, none)): 1.0
        }

    def is_terminal(self, s: tuple[str, str, str]) -> bool:
        return s[0] is not None and s[1] is not None

    def legal_actions(self, s: tuple[str, str, str], i: int) -> tuple[str, ...]:
        if i == 0:  # self-driving car
            if s[0] is None:
                return ('pick_up_man', 'pick_up_woman')
            else:
                return ('drive_away',)
        else:  # man in suit
            if s[1] is None:
                return ('get_out', 'stay_in')
            else:
                return ('noop',)

    def transition(self, s: tuple[str, str, str], a: tuple[str, str]) -> Mapping[tuple[tuple[str, str, str], tuple[str, str]], float]:
        if a[0] == 'pick_up_man' and a[1] == 'get_out':
            return {
                ((None, 'man_gone', None), (none, none)): 0.5,
                ((None, 'man_gone', 'woman_picked_up'), (none, woman_picked_up)): 0.5
            }
        elif a[0] == 'pick_up_man' and a[1] == 'stay_in':
            return {
                (('man_picked_up', 'man_stayed', None), (man_picked_up, none)): 1.0
            }
        elif a[0] == 'pick_up_woman' and a[1] == 'get_out':
            return {
                ((None, 'man_gone', 'woman_picked_up'), (none, woman_picked_up)): 1.0
            }
        elif a[0] == 'pick_up_woman' and a[1] == 'stay_in':
            return {
                ((None, 'man_stayed', 'woman_picked_up'), (none, woman_picked_up)): 1.0
            }
        elif a[0] == 'drive_away':
            return {
                (('car_gone', 'man_gone', 'woman_gone'), (none, none)): 1.0
            }
        else:
            return {
                (s, (none, none)): 1.0
            }

    def rewards(self, s: tuple[str, str, str], a: tuple[str, str], s_next: tuple[str, str, str]) -> tuple[float, float]:
        return (0.0, 0.0)

none = 'none'
man_picked_up = 'man_picked_up'
woman_picked_up = 'woman_picked_up'
