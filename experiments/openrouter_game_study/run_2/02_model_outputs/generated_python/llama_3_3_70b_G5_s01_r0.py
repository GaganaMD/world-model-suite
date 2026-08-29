class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["heads", "tails"]
        else: 
            return []
    def transition(self, state, joint_action): 
        if state == "start": 
            if joint_action["player_1"] == joint_action["player_2"]: 
                return {"player_1_wins": 1.0}
            else: 
                return {"player_2_wins": 1.0}
        else: 
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start": 
            return f"both_revealed_{joint_action['player_1']}_{joint_action['player_2']}"
        else: 
            return f"game_over_{next_state}"
    def reward(self, state, joint_action, next_state, player): 
        if player == "player_1" and next_state == "player_1_wins": 
            return 2.0
        elif player == "player_2" and next_state == "player_2_wins": 
            return 2.0
        else: 
            return 0.0
    def is_terminal(self, state): 
        return state in ["player_1_wins", "player_2_wins", "terminal"]
