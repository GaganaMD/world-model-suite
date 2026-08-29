class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["bid_low", "bid_high"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            v1 = "low" if joint_action["player_1"] == "bid_low" else "high"
            v2 = "low" if joint_action["player_2"] == "bid_low" else "high"
            if v1 == "low" and v2 == "low":
                return {"terminal": 1.0}
            elif v1 == "low" and v2 == "high":
                return {"terminal": 1.0}
            elif v1 == "high" and v2 == "low":
                return {"terminal": 1.0}
            else:
                return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            own_bid = joint_action[player]
            return f"bid={own_bid}"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state != "s0":
            return 0.0
        v1 = "low" if joint_action["player_1"] == "bid_low" else "high"
        v2 = "low" if joint_action["player_2"] == "bid_low" else "high"
        if player == "player_1":
            if v1 == "high" and v2 == "low":
                return 1.0
            elif v1 == "low" and v2 == "high":
                return -1.0
            elif v1 == "high" and v2 == "high":
                return 0.5
            else:
                return -0.5
        else:
            if v2 == "high" and v1 == "low":
                return 1.0
            elif v2 == "low" and v1 == "high":
                return -1.0
            elif v2 == "high" and v1 == "high":
                return 0.5
            else:
                return -0.5

    def is_terminal(self, state):
        return state == "terminal"
