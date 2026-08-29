from posg import POSG

class DroneDeliveryGate(POSG):
    """
    Player 0: drone
    Player 1: resident

    State tuple: (gate_status, resident_status, drone_status)
      gate_status: 'locked' | 'open'
      resident_status: 'away' | 'present'
      drone_status: 'at_gate' | 'departed'

    Terminal when drone_status == 'departed'.
    """
    n_players = 2

    def initial_distribution(self):
        # Gate is locked, resident is away, drone is at the gate.
        return {
            (('locked', 'away', 'at_gate'), ('locked', 'away')): 1.0,
        }

    def is_terminal(self, s):
        return s[2] == 'departed'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Drone can wait at the gate or depart.
            return ('wait', 'depart')
        else:
            # Resident can open the gate or do nothing.
            return ('open_gate', 'noop')

    def transition(self, s, a):
        gate_status, resident_status, drone_status = s
        drone_action, resident_action = a

        if drone_action == 'depart':
            next_state = (gate_status, resident_status, 'departed')
            obs = (drone_status, resident_status)
            return {(next_state, obs): 1.0}

        # Drone waits.
        if resident_action == 'open_gate':
            next_state = ('open', resident_status, 'at_gate')
            obs = ('open', resident_status)
        else:
            next_state = (gate_status, resident_status, 'at_gate')
            obs = (gate_status, resident_status)

        return {(next_state, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
