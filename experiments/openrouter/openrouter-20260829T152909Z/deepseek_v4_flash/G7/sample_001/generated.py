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
            return {"terminal": 1.0}
        return {}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0" and next_state == "terminal":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == "silent" and a2 == "silent":
                return "both_silent"
            elif a1 == "testify" and a2 == "testify":
                return "both_testify"
            elif a1 == "testify" and a2 == "silent":
                return "p1_testified_p2_silent"
            else:
                return "p1_silent_p2_testified"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0" and next_state == "terminal":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == "silent" and a2 == "silent":
                return -1.0
            elif a1 == "testify" and a2 == "testify":
                return -2.0
            elif a1 == "testify" and a2 == "silent":
                return 0.0 if player == "player_1" else -3.0
            else:
                return -3.0 if player == "player_1" else 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"