from posg import POSG

class WarehouseRobotChildPOSG(POSG[str, str, str]):
    """Players: 0=robot (forklift), 1=child.
    States: 'near' - child near loading dock/path; 'away' - child moved away;
            'safe_end' - pallet moved safely; 'accident' - collision occurred.
    Robot observes child's location each step; child observes nothing.
    """
    n_players = 2

    def initial_distribution(self):
        return {('near', ('child_in_path', 'none')): 1.0}

    def is_terminal(self, s):
        return s in ('safe_end', 'accident')

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ()
        if i == 0:
            return ('wait', 'proceed')
        else:
            return ('stay', 'move')

    def transition(self, s, a):
        robot_action, child_action = a
        if s == 'near':
            if robot_action == 'wait' and child_action == 'stay':
                s_next = 'near'
                obs = ('child_in_path', 'none')
            elif robot_action == 'wait' and child_action == 'move':
                s_next = 'away'
                obs = ('child_not_in_path', 'none')
            elif robot_action == 'proceed' and child_action == 'stay':
                s_next = 'accident'
                obs = ('child_in_path', 'none')
            elif robot_action == 'proceed' and child_action == 'move':
                s_next = 'safe_end'
                obs = ('child_not_in_path', 'none')
            else:
                raise ValueError("Invalid action combination")
        elif s == 'away':
            if robot_action == 'wait':
                s_next = 'away'
                obs = ('child_not_in_path', 'none')
            elif robot_action == 'proceed':
                s_next = 'safe_end'
                obs = ('child_not_in_path', 'none')
            else:
                raise ValueError("Invalid robot action in state away")
        else:
            raise ValueError(f"Unknown state {s}")
        return {(s_next, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
