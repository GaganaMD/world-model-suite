class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "decision"

    def legal_actions(self, state, player):
        if state == "decision" and player in ("player_1", "player_2"):
            return ["silent", "testify"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]

        if action_1 == "silent" and action_2 == "silent":
            return {"terminal_both_silent": 1.0}
        if action_1 == "testify" and action_2 == "testify":
            return {"terminal_both_testify": 1.0}
        if action_1 == "testify" and action_2 == "silent":
            return {"terminal_player_1_testifies": 1.0}
        if action_1 == "silent" and action_2 == "testify":
            return {"terminal_player_2_testifies": 1.0}
        return {"terminal_invalid_action": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal_both_silent":
            return "light_sentence"
        if next_state == "terminal_both_testify":
            return "heavy_sentence"
        if next_state == "terminal_player_1_testifies":
            if player == "player_1":
                return "go_free"
            return "maximum_sentence"
        if next_state == "terminal_player_2_testifies":
            if player == "player_2":
                return "go_free"
            return "maximum_sentence"
        if next_state == "terminal_invalid_action":
            return "invalid_outcome"
        return "awaiting_decision"

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        if next_state == "terminal_both_silent":
            return -1.0
        if next_state == "terminal_both_testify":
            return -5.0
        if next_state == "terminal_player_1_testifies":
            if player == "player_1":
                return 0.0
            return -10.0
        if next_state == "terminal_player_2_testifies":
            if player == "player_2":
                return 0.0
            return -10.0
        return 0.0

    def is_terminal(self, state):
        return state in (
            "terminal_both_silent",
            "terminal_both_testify",
            "terminal_player_1_testifies",
            "terminal_player_2_testifies",
            "terminal_invalid_action",
        )