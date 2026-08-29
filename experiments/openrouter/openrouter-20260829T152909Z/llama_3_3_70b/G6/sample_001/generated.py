class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "bidding"
    def legal_actions(self, state, player): 
        if state == "bidding":
            return ["low", "high"]
        else:
            return []
    def transition(self, state, joint_action): 
        if state == "bidding":
            if joint_action["player_1"] == joint_action["player_2"]:
                return {"won_by_player_1": 0.5, "won_by_player_2": 0.5}
            elif joint_action["player_1"] == "high" and joint_action["player_2"] == "low":
                return {"won_by_player_1": 1.0}
            else:
                return {"won_by_player_2": 1.0}
        else:
            return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "won_by_player_1":
            return "won" if player == "player_1" else "lost"
        elif next_state == "won_by_player_2":
            return "won" if player == "player_2" else "lost"
        else:
            return "bidding"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "won_by_player_1":
            return 1.0 if player == "player_1" else 0.0
        elif next_state == "won_by_player_2":
            return 1.0 if player == "player_2" else 0.0
        else:
            return 0.0
    def is_terminal(self, state): 
        return state != "bidding"