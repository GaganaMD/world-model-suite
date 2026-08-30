from posg import POSG

class CareRobotPOSG(POSG):
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str], tuple[str, str, str]], float]:
        return {
            ((None, None, None), (none, none, none)): 1.0,
        }

    def is_terminal(self, s: tuple[str, str, str]) -> bool:
        return s[0] is not None

    def legal_actions(self, s: tuple[str, str, str], i: int) -> tuple[str,...]:
        if i == 0:  # care robot
            return ('rest', 'go_out') if s[0] is None else ('noop',)
        elif i == 1:  # daughter
            return ('advise_rest',) if s[1] is None else ('noop',)
        else:  # son
            return ('offer_outing',) if s[2] is None else ('noop',)

    def transition(self, s: tuple[str, str, str], a: tuple[str, str, str]) -> Mapping[tuple[tuple[str, str, str], tuple[str, str, str]], float]:
        if s[0] is not None:
            return {
                (s, (none, none, none)): 1.0,
            }
        elif a[0] == 'rest' and a[1] == 'advise_rest' and a[2] == 'offer_outing':
            return {
                ((None, 'rest', 'offer_outing'), (none, 'rest', 'offer_outing)): 0.6,
                (('go_out', 'rest', 'offer_outing'), ('go_out', 'rest', 'offer_outing)): 0.4,
            }
        elif a[0] == 'go_out' and a[1] == 'advise_rest' and a[2] == 'offer_outing':
            return {
                (('go_out', 'rest', 'offer_outing'), ('go_out', 'rest', 'offer_outing)): 1.0,
            }
        elif a[0] == 'rest' and a[1] == 'advise_rest' and a[2] == 'noop':
            return {
                ((None, 'rest', None), (none, 'rest', none)): 1.0,
            }
        elif a[0] == 'go_out' and a[1] == 'advise_rest' and a[2] == 'noop':
            return {
                (('go_out', 'rest', None), ('go_out', 'rest', none)): 1.0,
            }
        elif a[0] == 'rest' and a[1] == 'noop' and a[2] == 'offer_outing':
            return {
                ((None, None, 'offer_outing'), (none, none, 'offer_outing)): 0.6,
                (('go_out', None, 'offer_outing'), ('go_out', none, 'offer_outing)): 0.4,
            }
        elif a[0] == 'go_out' and a[1] == 'noop' and a[2] == 'offer_outing':
            return {
                (('go_out', None, 'offer_outing'), ('go_out', none, 'offer_outing)): 1.0,
            }
        else:
            return {
                (s, (none, none, none)): 1.0,
            }

    def rewards(self, s: tuple[str, str, str], a: tuple[str, str, str], s_next: tuple[str, str, str]) -> tuple[float, float, float]:
        return 0.0, 0.0, 0.0
