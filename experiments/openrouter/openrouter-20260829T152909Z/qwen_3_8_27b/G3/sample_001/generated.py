class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if player not in ("player_1", "player_2"):
            return []
        if self.is_terminal(state):
            return []
        return ["heads", "tails"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        return {"coin_heads": 0.5, "coin_tails": 0.5}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "coin_heads":
            return "heads"
        if next_state == "coin_tails":
            return "tails"
        return "pre_flip"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "coin_heads":
            result = "heads"
        elif next_state == "coin_tails":
            result = "tails"
        else:
            return 0.0

        if player == "player_1":
            other_player = "player_2"
        elif player == "player_2":
            other_player = "player_1"
        else:
            return 0.0

        my_call = joint_action.get(player)
        other_call = joint_action.get(other_player)

        if my_call == result:
            if other_call == result:
                return 0.0
            return 1.0

        if other_call == result:
            return -1.0

        return 0.0

    def is_terminal(self, state):
        return state in ("coin_heads", "coin_tails")