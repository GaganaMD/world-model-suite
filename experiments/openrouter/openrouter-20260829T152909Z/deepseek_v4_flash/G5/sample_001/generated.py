class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "initial"

    def legal_actions(self, state, player):
        if state == "initial":
            return ["heads", "tails"]
        return []

    def transition(self, state, joint_action):
        if state == "initial":
            return {"terminal": 1.0}
        return {}

    def observation(self, state, joint_action, next_state, player):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        return f"{a1}_{a2}"

    def reward(self, state, joint_action, next_state, player):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        if a1 == a2:
            return 2.0 if player == "player_1" else 0.0
        else:
            return 0.0 if player == "player_1" else 2.0

    def is_terminal(self, state):
        return state == "terminal"