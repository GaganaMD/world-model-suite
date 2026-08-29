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
            p1_val = "low" if joint_action["player_1"] == "bid_low" else "high"
            p2_val = "low" if joint_action["player_2"] == "bid_low" else "high"
            p1_bid = 1 if joint_action["player_1"] == "bid_low" else 2
            p2_bid = 1 if joint_action["player_2"] == "bid_low" else 2

            if p1_bid > p2_bid:
                winner = "player_1"
            elif p2_bid > p1_bid:
                winner = "player_2"
            else:
                winner = "player_1" if (hash((p1_val, p2_val)) % 2 == 0) else "player_2"

            if winner == "player_1":
                next_state = f"t1_{p1_val}_{p2_val}"
            else:
                next_state = f"t2_{p1_val}_{p2_val}"
            return {next_state: 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            if player == "player_1":
                return f"obs_p1_{joint_action['player_1']}"
            else:
                return f"obs_p2_{joint_action['player_2']}"
        return f"obs_{player}_{next_state}"

    def reward(self, state, joint_action, next_state, player):
        if state != "s0":
            return 0.0

        p1_val = "low" if joint_action["player_1"] == "bid_low" else "high"
        p2_val = "low" if joint_action["player_2"] == "bid_low" else "high"
        p1_bid = 1 if joint_action["player_1"] == "bid_low" else 2
        p2_bid = 1 if joint_action["player_2"] == "bid_low" else 2

        if p1_bid > p2_bid:
            winner = "player_1"
        elif p2_bid > p1_bid:
            winner = "player_2"
        else:
            winner = "player_1" if (hash((p1_val, p2_val)) % 2 == 0) else "player_2"

        if player == "player_1":
            if winner == "player_1":
                value = 10 if p1_val == "high" else 5
                return value - p1_bid
            else:
                return 0.0
        else:
            if winner == "player_2":
                value = 10 if p2_val == "high" else 5
                return value - p2_bid
            else:
                return 0.0

    def is_terminal(self, state):
        return state.startswith("t1_") or state.startswith("t2_")
