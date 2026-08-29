class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["stay_silent", "testify"]
    def transition(self, state, joint_action): 
        if joint_action["player_1"] == "stay_silent" and joint_action["player_2"] == "stay_silent":
            return {"light_sentence": 1.0}
        elif joint_action["player_1"] == "testify" and joint_action["player_2"] == "testify":
            return {"heavy_sentence": 1.0}
        elif joint_action["player_1"] == "testify" and joint_action["player_2"] == "stay_silent":
            return {"player_1_free": 1.0}
        elif joint_action["player_1"] == "stay_silent" and joint_action["player_2"] == "testify":
            return {"player_2_free": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "light_sentence":
            return "both_stay_silent"
        elif next_state == "heavy_sentence":
            return "both_testify"
        elif next_state == "player_1_free":
            return "player_1_testify"
        elif next_state == "player_2_free":
            return "player_2_testify"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "light_sentence":
            return 1.0
        elif next_state == "heavy_sentence":
            return -2.0
        elif next_state == "player_1_free" and player == "player_1":
            return 3.0
        elif next_state == "player_1_free" and player == "player_2":
            return -3.0
        elif next_state == "player_2_free" and player == "player_1":
            return -3.0
        elif next_state == "player_2_free" and player == "player_2":
            return 3.0
    def is_terminal(self, state): 
        return state in ["light_sentence", "heavy_sentence", "player_1_free", "player_2_free"]