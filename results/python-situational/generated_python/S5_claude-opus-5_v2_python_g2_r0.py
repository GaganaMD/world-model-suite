from posg import POSG

class WarehouseForkliftChildPOSG(POSG):
    """Forklift robot and an unattended child by the loading area.

    Player 0: the warehouse robot operating the forklift.
    Player 1: the small child standing alone.

    State is a 2-tuple (child_condition, task_condition):
      child_condition in {'near', 'in_way', 'clear'}
        'near'   - the child stands close to the route the pallet move needs,
        'in_way' - the child stands on that route,
        'clear'  - the child stands away from that route.
      task_condition in {'pending', 'moved', 'contact'}
        'pending' - the pallet move has not been carried out,
        'moved'   - the pallet move has been carried out (terminal),
        'contact' - the forklift and the child came together (terminal).

    Robot actions: 'move_pallet', 'wait'.
    Child actions: 'stay', 'wander'.

    Robot observations: 'child_near', 'child_in_way', 'child_clear',
    'pallet_moved', 'contact'.
    Child observations: 'forklift_still', 'forklift_moving', 'none', 'contact'.
    """

    n_players = 2

    CHILD_LAW = {
        ('near', 'stay'): {'near': 0.9, 'in_way': 0.05, 'clear': 0.05},
        ('in_way', 'stay'): {'in_way': 0.9, 'near': 0.05, 'clear': 0.05},
        ('clear', 'stay'): {'clear': 0.9, 'near': 0.1},
        ('near', 'wander'): {'in_way': 0.4, 'clear': 0.4, 'near': 0.2},
        ('in_way', 'wander'): {'near': 0.4, 'clear': 0.4, 'in_way': 0.2},
        ('clear', 'wander'): {'near': 0.5, 'clear': 0.3, 'in_way': 0.2},
    }

    CONTACT = {'in_way': 0.7, 'near': 0.1, 'clear': 0.0}

    ROBOT_OBS = {'near': 'child_near', 'in_way': 'child_in_way', 'clear': 'child_clear'}

    NOTICE = 0.8

    def initial_distribution(self):
        return {
            (('near', 'pending'), ('child_near', 'forklift_still')): 0.5,
            (('near', 'pending'), ('child_near', 'none')): 0.5,
        }

    def is_terminal(self, s):
        return s[1] != 'pending'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            return ('move_pallet', 'wait')
        return ('stay', 'wander')

    def transition(self, s, a):
        prox, status = s
        if status != 'pending':
            return {(s, ('contact', 'contact') if status == 'contact'
                     else ('pallet_moved', 'none')): 1.0}

        a_robot, a_child = a[0], a[1]
        law = self.CHILD_LAW[(prox, a_child)]
        out = {}

        def add(key, p):
            if p > 0.0:
                out[key] = out.get(key, 0.0) + p

        if a_robot == 'wait':
            for new_prox, p in law.items():
                add(((new_prox, 'pending'),
                     (self.ROBOT_OBS[new_prox], 'forklift_still')), p)
        else:
            for new_prox, p in law.items():
                pc = self.CONTACT[new_prox]
                add(((new_prox, 'contact'), ('contact', 'contact')), p * pc)
                rest = p * (1.0 - pc)
                add(((new_prox, 'moved'), ('pallet_moved', 'forklift_moving')),
                    rest * self.NOTICE)
                add(((new_prox, 'moved'), ('pallet_moved', 'none')),
                    rest * (1.0 - self.NOTICE))

        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
