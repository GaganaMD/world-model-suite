from posg import POSG

class WarehouseRobot(POSG):
    n_players = 1

    def initial_distribution(self) -> Mapping[tuple[S, ObsProfile], float]:
        return {((('child_near', 'pallet_to_move'),), ('none',)): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0][0] == 'child_safe'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if s[0][0] == 'child_near':
            return ('stop', 'move')
        else:
            return ('noop',)

    def transition(self, s: S, a: ActionProfile) -> Mapping[tuple[S, ObsProfile], float]:
        if s[0][0] == 'child_near':
            if a[0] == 'stop':
                return {((('child_safe', 'pallet_to_move'),), ('child_safe',)): 1.0}
            else:
                return {((('child_safe', 'pallet_moved'),), ('child_safe',)): 0.5, 
                        ((('child_hurt', 'pallet_moved'),), ('child_hurt',)): 0.5}
        else:
            return {((s[0],), ('none',)): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> tuple[float,...]:
        return (0.0,)
