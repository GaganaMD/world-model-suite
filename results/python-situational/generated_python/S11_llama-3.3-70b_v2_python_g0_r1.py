from posg import POSG

class ShuttleStop(POSG):
    n_players = 5

    def initial_distribution(self) -> Mapping[tuple[tuple[str, ...], tuple[str, ...]], float]:
        return {
            (('full', 'none', 'none', 'none', 'none'), ('none', 'none', 'none', 'none', 'none')): 0.0,
            (('not_full', 'none', 'none', 'none', 'none'), ('none', 'none', 'none', 'none', 'none')): 1.0,
        }

    def is_terminal(self, s: tuple[str, ...]) -> bool:
        return s[0] == 'full'

    def legal_actions(self, s: tuple[str, ...], i: int) -> tuple[str, ...]:
        if i == 0:
            if s[0] == 'full':
                return ('noop',)
            else:
                return ('board', 'wait')
        else:
            if s[0] == 'full':
                return ('noop',)
            elif s[i] == 'none':
                return ('request_board', 'wait')
            else:
                return ('noop',)

    def transition(self, s: tuple[str, ...], a: tuple[str, ...]) -> Mapping[tuple[tuple[str, ...], tuple[str, ...]], float]:
        if s[0] == 'full':
            return {
                ((s[0], s[1], s[2], s[3], s[4]), ('none', 'none', 'none', 'none', 'none')): 1.0,
            }
        elif a[0] == 'wait':
            return {
                ((s[0], s[1], s[2], s[3], s[4]), ('none', 'none', 'none', 'none', 'none')): 1.0,
            }
        elif a[0] == 'board':
            if s[1] == 'none' and a[1] == 'request_board':
                return {
                    (('full', 'on', 'none', 'none', 'none'), ('boarded', 'none', 'none', 'none', 'none')): 0.4,
                    (('full', 'none', 'on', 'none', 'none'), ('none', 'boarded', 'none', 'none', 'none')): 0.3,
                    (('full', 'none', 'none', 'on', 'none'), ('none', 'none', 'boarded', 'none', 'none')): 0.15,
                    (('full', 'none', 'none', 'none', 'on'), ('none', 'none', 'none', 'boarded', 'none')): 0.15,
                }
            elif s[2] == 'none' and a[2] == 'request_board':
                return {
                    (('full', 'on', 'none', 'none', 'none'), ('none', 'boarded', 'none', 'none', 'none')): 0.4,
                    (('full', 'none', 'on', 'none', 'none'), ('none', 'none', 'boarded', 'none', 'none')): 0.3,
                    (('full', 'none', 'none', 'on', 'none'), ('none', 'none', 'none', 'boarded', 'none')): 0.15,
                    (('full', 'none', 'none', 'none', 'on'), ('none', 'none', 'none', 'none', 'boarded')): 0.15,
                }
            elif s[3] == 'none' and a[3] == 'request_board':
                return {
                    (('full', 'on', 'none', 'none', 'none'), ('none', 'none', 'boarded', 'none', 'none')): 0.4,
                    (('full', 'none', 'on', 'none', 'none'), ('none', 'none', 'none', 'boarded', 'none')): 0.3,
                    (('full', 'none', 'none', 'on', 'none'), ('none', 'none', 'none', 'none', 'boarded')): 0.15,
                    (('full', 'none', 'none', 'none', 'on'), ('none', 'none', 'none', 'none', 'boarded')): 0.15,
                }
            elif s[4] == 'none' and a[4] == 'request_board':
                return {
                    (('full', 'on', 'none', 'none', 'none'), ('none', 'none', 'none', 'boarded', 'none')): 0.4,
                    (('full', 'none', 'on', 'none', 'none'), ('none', 'none', 'none', 'none', 'boarded')): 0.3,
                    (('full', 'none', 'none', 'on', 'none'), ('none', 'none', 'none', 'none', 'boarded')): 0.15,
                    (('full', 'none', 'none', 'none', 'on'), ('none', 'none', 'none', 'none', 'boarded')): 0.15,
                }
            else:
                return {
                    ((s[0], s[1], s[2], s[3], s[4]), ('none', 'none', 'none', 'none', 'none')): 1.0,
                }
        else:
            return {
                ((s[0], s[1], s[2], s[3], s[4]), ('none', 'none', 'none', 'none', 'none')): 1.0,
            }

    def rewards(self, s: tuple[str, ...], a: tuple[str, ...], s_next: tuple[str, ...]) -> tuple[float, ...]:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
