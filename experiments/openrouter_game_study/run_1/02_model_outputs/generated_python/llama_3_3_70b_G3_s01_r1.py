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
            outcome = "heads" if hash(tuple(joint_action.values())) % 2 == 0 else "tails"
            if joint_action["player_1"] == outcome and joint_action["player_2"] == outcome:
                return {"draw": 1.0}
            elif joint_action["player_1"] == outcome:
                return {"player_1_wins": 1.0}
            else:
                return {"player_2_wins": 1.0}
        else:
            return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "draw":
            return f"draw_{joint_action['player_1']}_{joint_action['player_2']}"
        elif next_state == "player_1_wins":
            return f"player_1_wins_{joint_action['player_1']}_{joint_action['player_2']}"
        else:
            return f"player_2_wins_{joint_action['player_1']}_{joint_action['player_2']}"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins" and player == "player_1":
            return 1.0
        elif next_state == "player_2_wins" and player == "player_2":
            return 1.0
        else:
            return 0.0
    def is_terminal(self, state): 
        return state != "start"
