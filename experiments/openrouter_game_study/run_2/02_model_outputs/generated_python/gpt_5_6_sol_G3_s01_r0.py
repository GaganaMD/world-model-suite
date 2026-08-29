class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["heads", "tails"]

    def transition(self, state, joint_action):
        if state == "s0":
            return {"coin_heads": 0.5, "coin_tails": 0.5}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "coin_heads":
            return "coin_heads"
        if next_state == "coin_tails":
            return "coin_tails"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state != "s0":
            return 0.0
        result = "heads" if next_state == "coin_heads" else "tails"
        own_match = joint_action[player] == result
        other = "player_2" if player == "player_1" else "player_1"
        other_match = joint_action[other] == result
        if own_match and not other_match:
            return 1.0
        if other_match and not own_match:
            return -1.0
        return 0.0

    def is_terminal(self, state):
        return state == "coin_heads" or state == "coin_tails" or state == "terminal"
