class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["Commander1", "Commander2"]

    def initial_state(self):
        return {}

    def legal_actions(self, state, player):
        return {0: 3, 1: 2, 2: 1, 3: 0}

    def transition(self, state, joint_action):
        battlefield1 = joint_action["Commander1"] + joint_action["Commander2"]
        battlefield2 = abs(joint_action["Commander1"] - joint_action["Commander2"])
        next_state = {battlefield1: 1, battlefield2: 1}
        return next_state

    def observation(self, state, joint_action, next_state, player):
        return next_state

    def reward(self, state, joint_action, next_state, player):
        if next_state[0] > next_state[1]:
            return 1 if player == "Commander1" else -1
        elif next_state[0] < next_state[1]:
            return -1 if player == "Commander1" else 1
        else:
            return 0

    def is_terminal(self, state):
        return True