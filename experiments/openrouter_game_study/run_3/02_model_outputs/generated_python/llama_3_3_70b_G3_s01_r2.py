class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["heads", "tails"]
    def transition(self, state, joint_action): 
        if state == "s0":
            return {"s1": 0.5, "s2": 0.5}
        elif state == "s1":
            if joint_action["player_1"] == "heads" and joint_action["player_2"] == "heads":
                return {"draw": 1.0}
            elif joint_action["player_1"] == "heads" and joint_action["player_2"] == "tails":
                return {"player_1_wins": 1.0}
            elif joint_action["player_1"] == "tails" and joint_action["player_2"] == "heads":
                return {"player_2_wins": 1.0}
            else:
                return {"draw": 1.0}
        elif state == "s2":
            if joint_action["player_1"] == "tails" and joint_action["player_2"] == "tails":
                return {"draw": 1.0}
            elif joint_action["player_1"] == "tails" and joint_action["player_2"] == "heads":
                return {"player_1_wins": 1.0}
            elif joint_action["player_1"] == "heads" and joint_action["player_2"] == "tails":
                return {"player_2_wins": 1.0}
            else:
                return {"draw": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        return f"{state}_{joint_action['player_1']}_{joint_action['player_2']}_{next_state}"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins" and player == "player_1":
            return 1.0
        elif next_state == "player_2_wins" and player == "player_2":
            return 1.0
        elif next_state == "draw":
            return 0.0
        else:
            return -1.0
    def is_terminal(self, state): 
        return state in ["player_1_wins", "player_2_wins", "draw"]
