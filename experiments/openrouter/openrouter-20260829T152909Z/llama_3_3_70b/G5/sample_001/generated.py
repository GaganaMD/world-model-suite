class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): 
        return ["player_1", "player_2"]

    def initial_state(self): 
        return "s0"

    def legal_actions(self, state, player): 
        return ["heads", "tails"]

    def transition(self, state, joint_action): 
        if joint_action["player_1"] == joint_action["player_2"]:
            return {"terminal_same": 1.0}
        else:
            return {"terminal_different": 1.0}

    def observation(self, state, joint_action, next_state, player): 
        if next_state == "terminal_same":
            return "same"
        else:
            return "different"

    def reward(self, state, joint_action, next_state, player): 
        if next_state == "terminal_same" and player == "player_1":
            return 2.0
        elif next_state == "terminal_different" and player == "player_2":
            return 2.0
        else:
            return 0.0

    def is_terminal(self, state): 
        return state in ["terminal_same", "terminal_different"]