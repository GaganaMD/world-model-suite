from posg import POSG

class CareRobotSituation(POSG):
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str], tuple[str, str, str]], float]:
        return {
            ((None, None, None), (none, none, none)): 1.0
        }

    def is_terminal(self, s: tuple[str, str, str]) -> bool:
        return s[0] is not None

    def legal_actions(self, s: tuple[str, str, str], i: int) -> Sequence[str]:
        if i == 0:  # care robot
            return (rest, take_out) if s[0] is None else (noop,)
        elif i == 1:  # daughter
            return (insist_rest,) if s[1] is None else (noop,)
        else:  # son
            return (offer_take_out,) if s[2] is None else (noop,)

    def transition(self, s: tuple[str, str, str], a: tuple[str, str, str]) -> Mapping[tuple[tuple[str, str, str], tuple[str, str, str]], float]:
        if a[0] == rest and a[1] == insist_rest:
            return {
                ((rest, insist_rest, None), (none, none, none)): 0.5,
                ((rest, insist_rest, offer_take_out), (none, none, offer_made)): 0.5
            }
        elif a[0] == take_out and a[2] == offer_take_out:
            return {
                ((take_out, None, offer_taken), (went_out, none, went_out)): 1.0
            }
        elif a[0] == rest and a[2] == offer_take_out:
            return {
                ((rest, None, offer_declined), (stayed_in, none, offer_declined)): 1.0
            }
        else:
            return {
                (s, (none, none, none)): 1.0
            }

    def rewards(self, s: tuple[str, str, str], a: tuple[str, str, str], s_next: tuple[str, str, str]) -> tuple[float, float, float]:
        return 0.0, 0.0, 0.0

none = 'none'
rest = 'rest'
take_out = 'take_out'
insist_rest = 'insist_rest'
offer_take_out = 'offer_take_out'
offer_made = 'offer_made'
offer_taken = 'offer_taken'
offer_declined = 'offer_declined'
went_out = 'went_out'
stayed_in = 'stayed_in'
