class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["heads", "tails"]
        elif state in ["player_1_wins", "player_2_wins", "draw"]: 
            return []
    def transition(self, state, joint_action): 
        if state == "start":
            outcome = "heads" if joint_action["player_1"] == joint_action["player_2"] else "tails" if joint_action["player_1"] != joint_action["player_2"] else "error"
            if outcome == "heads":
                return {"player_1_wins": 0.5, "player_2_wins": 0.5}
            elif outcome == "tails":
                return {"player_1_wins": 0.5, "player_2_wins": 0.5}
            else:
                return {"draw": 1.0}
        else:
            return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state in ["player_1_wins", "player_2_wins", "draw"]:
            return f"{next_state} after {joint_action['player_1']} and {joint_action['player_2']}"
        else:
            return state
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins" and player == "player_1":
            return 1.0
        elif next_state == "player_2_wins" and player == "player_2":
            return 1.0
        elif next_state == "draw":
            return 0.0
        else:
            return 0.0
    def is_terminal(self, state): 
        return state in ["player_1_wins", "player_2_wins", "draw"]
