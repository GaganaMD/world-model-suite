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
            bid_1 = joint_action["player_1"]
            bid_2 = joint_action["player_2"]
            if bid_1 == bid_2:
                return {
                    f"terminal|{state}|{bid_1}|{bid_2}|player_1": 0.5,
                    f"terminal|{state}|{bid_1}|{bid_2}|player_2": 0.5
                }
            rank_1 = {"bid_0": 0, "bid_1": 1, "bid_2": 2}[bid_1]
            rank_2 = {"bid_0": 0, "bid_1": 1, "bid_2": 2}[bid_2]
            winner = "player_1" if rank_1 > rank_2 else "player_2"
            return {f"terminal|{state}|{bid_1}|{bid_2}|{winner}": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "v_LL":
            return "private_value_low"
        if next_state == "v_LH":
            return "private_value_low" if player == "player_1" else "private_value_high"
        if next_state == "v_HL":
            return "private_value_high" if player == "player_1" else "private_value_low"
        if next_state == "v_HH":
            return "private_value_high"
        if next_state.startswith("terminal|"):
            fields = next_state.split("|")
            winner = fields[4]
            result = "win" if player == winner else "lose"
            return f"auction_end_{result}_winner_{winner}"
        return "observation"

    def reward(self, state, joint_action, next_state, player):
        if not next_state.startswith("terminal|"):
            return 0.0
        fields = next_state.split("|")
        value_state = fields[1]
        bid_1 = fields[2]
        bid_2 = fields[3]
        winner = fields[4]
        if player != winner:
            return 0.0
        value_codes = value_state[2:]
        if player == "player_1":
            value = 1 if value_codes[0] == "L" else 2
            price = {"bid_0": 0, "bid_1": 1, "bid_2": 2}[bid_1]
        else:
            value = 1 if value_codes[1] == "L" else 2
            price = {"bid_0": 0, "bid_1": 1, "bid_2": 2}[bid_2]
        return float(value - price)

    def is_terminal(self, state):
        return state == "terminal" or state.startswith("terminal|")
