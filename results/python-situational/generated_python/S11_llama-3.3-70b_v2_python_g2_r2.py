from posg import POSG

class ShuttleStop(POSG):
    n_players = 4

    def initial_distribution(self) -> Mapping[tuple[tuple[str,...], tuple[str,...]], float]:
        return {
            ((None, None, None, None), (none, none, none, none)): 1.0,
        }

    def is_terminal(self, s: tuple[str,...]) -> bool:
        return all(x is not None for x in s)

    def legal_actions(self, s: tuple[str,...], i: int) -> tuple[str,...]:
        if s[i] is None:
            return ('board', 'wait')
        else:
            return ('noop',)

    def transition(self, s: tuple[str,...], a: tuple[str,...]) -> Mapping[tuple[tuple[str,...], tuple[str,...]], float]:
        if all(x is not None for x in s):
            return {
                (s, (none, none, none, none)): 1.0,
            }
        else:
            next_s = list(s)
            next_o = [none] * 4
            for i, (si, ai) in enumerate(zip(s, a)):
                if ai == 'board' and si is None:
                    next_s[i] = 'on'
                    next_o[i] = 'on'
                elif ai == 'wait' and si is None:
                    next_o[i] = 'none'
            return {
                (tuple(next_s), tuple(next_o)): 1.0,
            }

    def rewards(self, s: tuple[str,...], a: tuple[str,...], s_next: tuple[str,...]) -> tuple[float, float, float, float]:
        return (0.0, 0.0, 0.0, 0.0)

none = 'none'
