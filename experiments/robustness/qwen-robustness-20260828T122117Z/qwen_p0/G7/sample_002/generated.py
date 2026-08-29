class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("stay_silent", "stay_silent")
    def legal_actions(self, state, player): return ["stay_silent", "testify"]
    def transition(self, state, joint_action):
        if joint_action == ("stay_silent", "stay_silent"):
            return {"(stay_silent, stay_silent)": 1.0}
        elif joint_action == ("stay_silent", "testify"):
            return {"(stay_silent, testify)": 1.0}
        elif joint_action == ("testify", "stay_silent"):
            return {"(testify, stay_silent)": 1.0}
        elif joint_action == ("testify", "testify"):
            return {"(testify, testify)": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if player == "player_1":
            if joint_action[0] == "stay_silent" and joint_action[1] == "stay_silent":
                return "both_stay_silent"
            elif joint_action[0] == "stay_silent" and joint_action[1] == "testify":
                return "player_2_testifies"
            elif joint_action[0] == "testify" and joint_action[1] == "stay_silent":
                return "player_1_testifies"
            elif joint_action[0] == "testify" and joint_action[1] == "testify":
                return "both_testify"
        else:
            if joint_action[0] == "stay_silent" and joint_action[1] == "stay_silent":
                return "both_stay_silent"
            elif joint_action[0] == "stay_silent" and joint_action[1] == "testify":
                return "player_2_testifies"
            elif joint_action[0] == "testify" and joint_action[1] == "stay_silent":
                return "player_1_testifies"
            elif joint_action[0] == "testify" and joint_action[1] == "testify":
                return "both_testify"
    def reward(self, state, joint_action, next_state, player):
        if joint_action == ("stay_silent", "stay_silent"):
            return 1.0
        elif joint_action == ("stay_silent", "testify") or joint_action == ("testify", "stay_silent"):
            return -3.0
        elif joint_action == ("testify", "testify"):
            return -2.0
    def is_terminal(self, state): return state[0] != "stay_silent" and state[1] != "stay_silent"