class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["silent", "testify"]
        return []

    def transition(self, state, joint_action):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == "silent" and a2 == "silent":
                return {"terminal": 1.0}
            elif a1 == "testify" and a2 == "testify":
                return {"terminal": 1.0}
            elif a1 == "testify" and a2 == "silent":
                return {"terminal": 1.0}
            elif a1 == "silent" and a2 == "testify":
                return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == "silent" and a2 == "silent":
                return "both_silent"
            elif a1 == "testify" and a2 == "testify":
                return "both_testify"
            elif a1 == "testify" and a2 == "silent":
                return "p1_testify_p2_silent"
            elif a1 == "silent" and a2 == "testify":
                return "p1_silent_p2_testify"
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == "silent" and a2 == "silent":
                return -1.0
            elif a1 == "testify" and a2 == "testify":
                return -5.0
            elif a1 == "testify" and a2 == "silent":
                if player == "player_1":
                    return 0.0
                else:
                    return -10.0
            elif a1 == "silent" and a2 == "testify":
                if player == "player_1":
                    return -10.0
                else:
                    return 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
