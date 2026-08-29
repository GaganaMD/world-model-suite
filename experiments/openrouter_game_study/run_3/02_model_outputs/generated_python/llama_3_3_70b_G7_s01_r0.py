class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["suspect_1", "suspect_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["stay_silent", "testify"]
    def transition(self, state, joint_action): 
        if joint_action["suspect_1"] == "stay_silent" and joint_action["suspect_2"] == "stay_silent":
            return {"s1": 1.0}
        elif joint_action["suspect_1"] == "testify" and joint_action["suspect_2"] == "testify":
            return {"s2": 1.0}
        elif joint_action["suspect_1"] == "testify" and joint_action["suspect_2"] == "stay_silent":
            return {"s3": 1.0}
        elif joint_action["suspect_1"] == "stay_silent" and joint_action["suspect_2"] == "testify":
            return {"s4": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "s1":
            return f"both_stay_silent"
        elif next_state == "s2":
            return f"both_testify"
        elif next_state == "s3":
            if player == "suspect_1":
                return f"suspect_1_testify_suspect_2_silent"
            else:
                return f"suspect_2_silent_suspect_1_testify"
        elif next_state == "s4":
            if player == "suspect_1":
                return f"suspect_1_silent_suspect_2_testify"
            else:
                return f"suspect_2_testify_suspect_1_silent"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "s1":
            return -1.0
        elif next_state == "s2":
            return -5.0
        elif next_state == "s3":
            if player == "suspect_1":
                return 0.0
            else:
                return -10.0
        elif next_state == "s4":
            if player == "suspect_1":
                return -10.0
            else:
                return 0.0
    def is_terminal(self, state): 
        return state in ["s1", "s2", "s3", "s4"]
