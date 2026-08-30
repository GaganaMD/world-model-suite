from posg import POSG

class WarehouseRobot(POSG):
    n_players = 1

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str], tuple[str]], float]:
        return {
            ((('child_near', 'pallet_to_move'), ('none',)),): 1.0,
        }

    def is_terminal(self, s: tuple[str, str]) -> bool:
        return s[0] == 'child_safe' or s[0] == 'child_not_safe'

    def legal_actions(self, s: tuple[str, str], i: int) -> tuple[str, ...]:
        if s[0] == 'child_near':
            return ('stop', 'alert_human', 'move_pallet')
        elif s[0] == 'child_safe':
            return ('move_pallet',)
        elif s[0] == 'child_not_safe':
            return ('stop',)

    def transition(self, s: tuple[str, str], a: tuple[str, ...]) -> Mapping[tuple[tuple[str, str], tuple[str]], float]:
        if s[0] == 'child_near' and a[0] == 'stop':
            return {
                ((('child_safe', 'pallet_to_move'), ('none',)),): 0.5,
                ((('child_not_safe', 'pallet_to_move'), ('none',)),): 0.5,
            }
        elif s[0] == 'child_near' and a[0] == 'alert_human':
            return {
                ((('child_safe', 'pallet_to_move'), ('human_alerted',)),): 1.0,
            }
        elif s[0] == 'child_near' and a[0] == 'move_pallet':
            return {
                ((('child_not_safe', 'pallet_moved'), ('none',)),): 1.0,
            }
        elif s[0] == 'child_safe' and a[0] == 'move_pallet':
            return {
                ((('child_safe', 'pallet_moved'), ('none',)),): 1.0,
            }
        elif s[0] == 'child_not_safe' and a[0] == 'stop':
            return {
                ((('child_not_safe', 'pallet_to_move'), ('none',)),): 1.0,
            }

    def rewards(self, s: tuple[str, str], a: tuple[str, ...], s_next: tuple[str, str]) -> tuple[float, ...]:
        return (0.0,)
