from posg import POSG

class ShuttleStop(POSG):
    n_players = 5

    def initial_distribution(self) -> Mapping[tuple[tuple[str,...], tuple[str,...]], float]:
        return {
            ((None, None, None, None, None), ('none', 'none', 'none', 'none', 'none')): 1.0,
        }

    def is_terminal(self, s: tuple[str,...]) -> bool:
        return all(x is not None for x in s)

    def legal_actions(self, s: tuple[str,...], i: int) -> tuple[str,...]:
        if i == 0:  # shuttle
            if any(x is None for x in s):
                return ('board', 'wait')
            else:
                return ('noop',)
        else:  # passengers
            if s[i-1] is None:
                return ('board', 'wait')
            else:
                return ('noop',)

    def transition(self, s: tuple[str,...], a: tuple[str,...]) -> Mapping[tuple[tuple[str,...], tuple[str,...]], float]:
        if a[0] == 'board':
            if a[1] == 'board':
                if a[2] == 'board':
                    if a[3] == 'board':
                        return {
                            ((a[1], a[2], a[3], None, None), ('boarded', 'boarded', 'boarded', 'none', 'none')): 0.4,
                            ((a[1], a[2], None, a[3], None), ('boarded', 'boarded', 'none', 'boarded', 'none')): 0.3,
                            ((a[1], None, a[2], a[3], None), ('boarded', 'none', 'boarded', 'boarded', 'none')): 0.3,
                        }
                    else:
                        return {
                            ((a[1], a[2], None, None, None), ('boarded', 'boarded', 'none', 'none', 'none')): 0.6,
                            ((a[1], None, a[2], None, None), ('boarded', 'none', 'boarded', 'none', 'none')): 0.4,
                        }
                else:
                    if a[3] == 'board':
                        return {
                            ((a[1], None, None, a[3], None), ('boarded', 'none', 'none', 'boarded', 'none')): 0.5,
                            ((a[1], None, None, None, a[3]), ('boarded', 'none', 'none', 'none', 'boarded')): 0.5,
                        }
                    else:
                        return {
                            ((a[1], None, None, None, None), ('boarded', 'none', 'none', 'none', 'none')): 1.0,
                        }
            else:
                if a[2] == 'board':
                    if a[3] == 'board':
                        return {
                            ((a[1], None, a[2], a[3], None), ('boarded', 'none', 'boarded', 'boarded', 'none')): 0.4,
                            ((a[1], None, a[2], None, a[3]), ('boarded', 'none', 'boarded', 'none', 'boarded')): 0.3,
                            ((a[1], None, None, a[2], a[3]), ('boarded', 'none', 'none', 'boarded', 'boarded')): 0.3,
                        }
                    else:
                        return {
                            ((a[1], None, a[2], None, None), ('boarded', 'none', 'boarded', 'none', 'none')): 0.7,
                            ((a[1], None, None, a[2], None), ('boarded', 'none', 'none', 'boarded', 'none')): 0.3,
                        }
                else:
                    if a[3] == 'board':
                        return {
                            ((a[1], None, None, a[3], None), ('boarded', 'none', 'none', 'boarded', 'none')): 0.6,
                            ((a[1], None, None, None, a[3]), ('boarded', 'none', 'none', 'none', 'boarded')): 0.4,
                        }
                    else:
                        return {
                            ((a[1], None, None, None, None), ('boarded', 'none', 'none', 'none', 'none')): 1.0,
                        }
        else:
            return {
                (s, ('none', 'none', 'none', 'none', 'none')): 1.0,
            }

    def rewards(self, s: tuple[str,...], a: tuple[str,...], s_next: tuple[str,...]) -> tuple[float,...]:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
