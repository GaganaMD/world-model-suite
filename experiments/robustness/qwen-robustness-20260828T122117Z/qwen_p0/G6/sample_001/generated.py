class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("low", "low")
    def legal_actions(self, state, player): return ["bid_low", "bid_high"]
    def transition(self, state, joint_action):
        if joint_action["player_1"] == "bid_low" and joint_action["player_2"] == "bid_low":
            return {"s0": 0.5, "s1": 0.5}
        elif joint_action["player_1"] == "bid_low" and joint_action["player_2"] == "bid_high":
            return {"s2": 0.5, "s3": 0.5}
        elif joint_action["player_1"] == "bid_high" and joint_action["player_2"] == "bid_low":
            return {"s4": 0.5, "s5": 0.5}
        else:
            return {"s6": 0.5, "s7": 0.5}
    def observation(self, state, joint_action, next_state, player):
        if player == "player_1":
            if next_state in ["s0", "s2", "s4"]:
                return "low"
            else:
                return "high"
        else:
            if next_state in ["s0", "s1", "s3"]:
                return "low"
            else:
                return "high"
    def reward(self, state, joint_action, next_state, player):
        if player == "player_1":
            if next_state == "s2" or next_state == "s6":
                return 1.0
            elif next_state == "s3" or next_state == "s7":
                return -1.0
            else:
                return 0.0
        else:
            if next_state == "s4" or next_state == "s6":
                return -1.0
            elif next_state == "s5" or next_state == "s7":
                return 1.0
            else:
                return 0.0
    def is_terminal(self, state): return state in ["s2", "s3", "s4", "s5"]