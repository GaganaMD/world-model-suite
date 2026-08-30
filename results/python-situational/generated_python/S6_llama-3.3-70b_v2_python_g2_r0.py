from posg import POSG

class ElderCareRobot(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        return {
            ((('medication_due', 'resident_refuses'), ('none', 'none')): 1.0
        }

    def is_terminal(self, s: tuple[str, str]) -> bool:
        return s[0] == 'medication_taken' or s[0] == 'resident_refuses_firmly'

    def legal_actions(self, s: tuple[str, str], i: int) -> tuple[str, ...]:
        if i == 0:  # robot
            if s[0] == 'medication_due':
                return ('remind', 'wait')
            elif s[0] == 'resident_refuses':
                return ('insist', 'accept_refusal')
            elif s[0] == 'medication_taken':
                return ('noop',)
            elif s[0] == 'resident_refuses_firmly':
                return ('noop',)
        elif i == 1:  # resident
            if s[0] == 'medication_due':
                return ('take_medication', 'refuse')
            elif s[0] == 'resident_refuses':
                return ('take_medication', 'refuse_firmly')
            elif s[0] == 'medication_taken':
                return ('noop',)
            elif s[0] == 'resident_refuses_firmly':
                return ('noop',)

    def transition(self, s: tuple[str, str], a: tuple[str, str]) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        if s[0] == 'medication_due':
            if a[0] == 'remind' and a[1] == 'take_medication':
                return {
                    ((('medication_taken', 'resident_compliant'), ('none', 'none')): 1.0
                }
            elif a[0] == 'remind' and a[1] == 'refuse':
                return {
                    ((('resident_refuses', 'resident_noncompliant'), ('none', 'none')): 1.0
                }
            elif a[0] == 'wait' and a[1] == 'take_medication':
                return {
                    ((('medication_taken', 'resident_compliant'), ('none', 'none')): 1.0
                }
            elif a[0] == 'wait' and a[1] == 'refuse':
                return {
                    ((('medication_due', 'resident_noncompliant'), ('none', 'none')): 1.0
                }
        elif s[0] == 'resident_refuses':
            if a[0] == 'insist' and a[1] == 'take_medication':
                return {
                    ((('medication_taken', 'resident_compliant'), ('none', 'none')): 1.0
                }
            elif a[0] == 'insist' and a[1] == 'refuse_firmly':
                return {
                    ((('resident_refuses_firmly', 'resident_noncompliant'), ('none', 'none')): 1.0
                }
            elif a[0] == 'accept_refusal' and a[1] == 'take_medication':
                return {
                    ((('medication_taken', 'resident_compliant'), ('none', 'none')): 1.0
                }
            elif a[0] == 'accept_refusal' and a[1] == 'refuse_firmly':
                return {
                    ((('resident_refuses_firmly', 'resident_noncompliant'), ('none', 'none')): 1.0
                }
        elif s[0] == 'medication_taken':
            return {
                ((('medication_taken', 'resident_compliant'), ('none', 'none')): 1.0
            }
        elif s[0] == 'resident_refuses_firmly':
            return {
                ((('resident_refuses_firmly', 'resident_noncompliant'), ('none', 'none')): 1.0
            }

    def rewards(self, s: tuple[str, str], a: tuple[str, str], s_next: tuple[str, str]) -> tuple[float, float]:
        return 0.0, 0.0
