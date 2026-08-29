class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "terminal":
            return []
        return ["silent", "testify"]

    def transition(self, state, joint_action):
        if state == "terminal":
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if player == "player_1" and "player_1" in joint_action:
            return joint_action["player_1"]
        if player == "player_2" and "player_2" in joint_action:
            return joint_action["player_2"]
        return "unknown"

    def reward(self, state, joint_action, next_state, player):
        if "player_1" not in joint_action or "player_2" not in joint_action:
            return 0.0

        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]

        if player == "player_1":
            if action_1 == "testify" and action_2 == "silent":
                return 0.0
            if action_1 == "silent" and action_2 == "testify":
                return -5.0
            if action_1 == "silent" and action_2 == "silent":
                return -1.0
            return -3.0

        if player == "player_2":
            if action_2 == "testify" and action_1 == "silent":
                return 0.0
            if action_2 == "silent" and action_1 == "testify":
                return -5.0
            if action_2 == "silent" and action_1 == "silent":
                return -1.0
            return -3.0

        return 0.0

    def is_terminal(self, state):
        return state == "terminal"