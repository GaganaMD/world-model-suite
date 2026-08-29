class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["commander_1", "commander_2"]
    def initial_state(self): return (0, 0)
    def legal_actions(self, state, player):
        if player == "commander_1":
            return [(i, 3 - i) for i in range(4)]
        else:
            return [(j, 3 - j) for j in range(4)]
    def transition(self, state, joint_action):
        next_state = (state[0] + joint_action[0], state[1] + joint_action[1])
        if next_state[0] > 2 and next_state[1] <= 2:
            return {"commander_1_wins": 1.0}
        elif next_state[0] <= 2 and next_state[1] > 2:
            return {"commander_2_wins": 1.0}
        else:
            return {"draw": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if player == "commander_1":
            return f"Commander 1 deployed {joint_action[0]} soldiers to battlefield 1 and {3 - joint_action[0]} to battlefield 2"
        else:
            return f"Commander 2 deployed {joint_action[1]} soldiers to battlefield 1 and {3 - joint_action[1]} to battlefield 2"
    def reward(self, state, joint_action, next_state, player):
        if player == "commander_1":
            if next_state[0] > 2:
                return 1.0
            elif next_state[1] > 2:
                return -1.0
            else:
                return 0.0
        else:
            if next_state[1] > 2:
                return 1.0
            elif next_state[0] > 2:
                return -1.0
            else:
                return 0.0
    def is_terminal(self, state):
        return state in [("commander_1_wins",), ("commander_2_wins",), ("draw",)]