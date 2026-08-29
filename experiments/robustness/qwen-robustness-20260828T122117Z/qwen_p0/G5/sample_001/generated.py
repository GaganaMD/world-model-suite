class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("H", "H")
    def legal_actions(self, state, player): return ["H", "T"]
    def transition(self, state, joint_action):
        if joint_action["player_1"] == joint_action["player_2"]:
            return {"terminal": 1.0}
        else:
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        return f"Player {player} sees {joint_action[player]}"
    def reward(self, state, joint_action, next_state, player):
        if joint_action["player_1"] == joint_action["player_2"]:
            if player == "player_1":
                return 1.0
            else:
                return -1.0
        else:
            if player == "player_2":
                return 1.0
            else:
                return -1.0
    def is_terminal(self, state): 
        return True