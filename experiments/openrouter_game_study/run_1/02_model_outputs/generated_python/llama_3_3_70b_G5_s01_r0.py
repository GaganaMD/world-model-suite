class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["heads", "tails"]
        elif state in ["player_1_heads", "player_1_tails"]:
            return ["heads", "tails"]
        else:
            return []
    def transition(self, state, joint_action): 
        if state == "start":
            return {"player_1_heads": 0.5, "player_1_tails": 0.5}
        elif state in ["player_1_heads", "player_1_tails"]:
            if joint_action["player_1"] == joint_action["player_2"]:
                return {"terminal": 1.0}
            else:
                return {"terminal": 1.0}
        else:
            return {}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start":
            return "game_start"
        elif state in ["player_1_heads", "player_1_tails"]:
            if player == "player_1":
                return f"player_1_{joint_action['player_1']}_player_2_{joint_action['player_2']}"
            else:
                return f"player_1_{joint_action['player_1']}_player_2_{joint_action['player_2']}"
        else:
            return "game_over"
    def reward(self, state, joint_action, next_state, player): 
        if state in ["player_1_heads", "player_1_tails"] and joint_action["player_1"] == joint_action["player_2"]:
            if player == "player_1":
                return 2.0
            else:
                return -2.0
        elif state in ["player_1_heads", "player_1_tails"] and joint_action["player_1"]!= joint_action["player_2"]:
            if player == "player_1":
                return -2.0
            else:
                return 2.0
        else:
            return 0.0
    def is_terminal(self, state): 
        return state == "terminal"
