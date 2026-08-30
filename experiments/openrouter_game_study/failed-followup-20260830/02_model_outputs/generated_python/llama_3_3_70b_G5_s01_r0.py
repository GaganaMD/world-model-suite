class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): 
        if state == "s0":
            return ["heads", "tails"]
        elif state in ["s1", "s2", "s3", "s4"]:
            return []
    def transition(self, state, joint_action): 
        if state == "s0":
            if joint_action["player_1"] == joint_action["player_2"]:
                return {"s1": 1.0}
            else:
                return {"s2": 1.0}
        elif state in ["s1", "s2"]:
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if state == "s0":
            return f"player {player} chose {joint_action[player]}"
        elif state in ["s1", "s2"]:
            if next_state == "s1":
                return f"both chose {joint_action['player_1']}, player 1 wins"
            else:
                return f"player 1 chose {joint_action['player_1']}, player 2 chose {joint_action['player_2']}, player 2 wins"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "s1":
            if player == "player_1":
                return 2.0
            else:
                return 0.0
        elif next_state == "s2":
            if player == "player_1":
                return 0.0
            else:
                return 2.0
    def is_terminal(self, state): return state == "terminal"
