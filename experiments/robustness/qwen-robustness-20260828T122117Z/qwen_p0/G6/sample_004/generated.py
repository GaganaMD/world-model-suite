class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("s0", None, None)
    def legal_actions(self, state, player):
        if state[0] == "s0":
            return ["low", "high"]
        elif state[0] == "s1" and player == "player_1":
            return ["flip"]
        else:
            return []
    def transition(self, state, joint_action):
        if state[0] == "s0":
            bid1, bid2 = joint_action["player_1"], joint_action["player_2"]
            if bid1 > bid2:
                return {"s2": 1.0}
            elif bid1 < bid2:
                return {"s3": 1.0}
            else:
                return {"s4": 0.5, "s5": 0.5}
        elif state[0] == "s1" and joint_action["player_1"] == "flip":
            if state[1] > state[2]:
                return {"terminal": 1.0}
            else:
                return {"terminal": 1.0}
        else:
            return {}
    def observation(self, state, joint_action, next_state, player):
        if state[0] == "s0":
            return f"player_{player}_bids_{joint_action[player]}"
        elif state[0] == "s1" and player == "player_1":
            return "coin_flip"
        else:
            return ""
    def reward(self, state, joint_action, next_state, player):
        if state[0] == "s2":
            return 1.0
        elif state[0] == "s3":
            return -1.0
        elif state[0] == "s4" and player == "player_1":
            return 0.5
        elif state[0] == "s4" and player == "player_2":
            return -0.5
        elif state[0] == "s5" and player == "player_1":
            return -0.5
        elif state[0] == "s5" and player == "player_2":
            return 0.5
        else:
            return 0.0
    def is_terminal(self, state): return state in ["terminal", "s2", "s3"]