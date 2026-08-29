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
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == "bid_low" and a2 == "bid_low":
                return {"tie_low": 0.5, "p1_wins_low": 0.25, "p2_wins_low": 0.25}
            elif a1 == "bid_low" and a2 == "bid_high":
                return {"p2_wins_mixed": 1.0}
            elif a1 == "bid_high" and a2 == "bid_low":
                return {"p1_wins_mixed": 1.0}
            else:
                return {"tie_high": 0.5, "p1_wins_high": 0.25, "p2_wins_high": 0.25}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if next_state == "tie_low":
                return "tie_low_coin_flip"
            elif next_state == "p1_wins_low":
                return "p1_wins_low"
            elif next_state == "p2_wins_low":
                return "p2_wins_low"
            elif next_state == "p2_wins_mixed":
                return "p2_wins_mixed"
            elif next_state == "p1_wins_mixed":
                return "p1_wins_mixed"
            elif next_state == "tie_high":
                return "tie_high_coin_flip"
            elif next_state == "p1_wins_high":
                return "p1_wins_high"
            elif next_state == "p2_wins_high":
                return "p2_wins_high"
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if next_state == "tie_low":
                return 0.0
            elif next_state == "p1_wins_low":
                return 1.0 if player == "player_1" else 0.0
            elif next_state == "p2_wins_low":
                return 1.0 if player == "player_2" else 0.0
            elif next_state == "p2_wins_mixed":
                return 1.0 if player == "player_2" else 0.0
            elif next_state == "p1_wins_mixed":
                return 1.0 if player == "player_1" else 0.0
            elif next_state == "tie_high":
                return 0.0
            elif next_state == "p1_wins_high":
                return 1.0 if player == "player_1" else 0.0
            elif next_state == "p2_wins_high":
                return 1.0 if player == "player_2" else 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
