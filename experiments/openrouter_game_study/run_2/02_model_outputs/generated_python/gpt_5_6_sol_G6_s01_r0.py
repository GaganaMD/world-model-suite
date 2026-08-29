class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["action"]
        if state in ["v_LL", "v_LH", "v_HL", "v_HH"]:
            return ["bid_0", "bid_1", "bid_2"]
        return ["action"]

    def transition(self, state, joint_action):
        if state == "s0":
            return {
                "v_LL": 0.25,
                "v_LH": 0.25,
                "v_HL": 0.25,
                "v_HH": 0.25
            }
        if state in ["v_LL", "v_LH", "v_HL", "v_HH"]:
            b1 = joint_action["player_1"]
            b2 = joint_action["player_2"]
            if b1 == b2:
                return {
                    f"terminal_{state}_{b1}_{b2}_p1": 0.5,
                    f"terminal_{state}_{b1}_{b2}_p2": 0.5
                }
            if b1 == "bid_2" or (b1 == "bid_1" and b2 == "bid_0"):
                return {f"terminal_{state}_{b1}_{b2}_p1": 1.0}
            return {f"terminal_{state}_{b1}_{b2}_p2": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "v_LL":
            return "value_low"
        if next_state == "v_LH":
            return "value_low" if player == "player_1" else "value_high"
        if next_state == "v_HL":
            return "value_high" if player == "player_1" else "value_low"
        if next_state == "v_HH":
            return "value_high"
        if next_state.startswith("terminal_"):
            winner = "player_1" if next_state.endswith("_p1") else "player_2"
            return f"auction_end_{winner}"
        return "observation"

    def reward(self, state, joint_action, next_state, player):
        if not next_state.startswith("terminal_"):
            return 0.0
        parts = next_state.split("_")
        value_state = parts[2]
        bid = int(parts[4][-1])
        winner = "player_1" if next_state.endswith("_p1") else "player_2"
        if player != winner:
            return 0.0
        if player == "player_1":
            value = 1 if value_state[2] == "L" else 2
        else:
            value = 1 if value_state[3] == "L" else 2
        return float(value - bid)

    def is_terminal(self, state):
        return state == "terminal" or state.startswith("terminal_")
