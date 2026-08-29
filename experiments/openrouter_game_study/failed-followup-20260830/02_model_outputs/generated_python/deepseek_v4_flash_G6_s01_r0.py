class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["low_bid", "medium_bid", "high_bid"]
        if state == "terminal":
            return ["noop"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            bid1 = joint_action["player_1"]
            bid2 = joint_action["player_2"]
            bid_values = {
                "low_bid": 1.0,
                "medium_bid": 2.0,
                "high_bid": 3.0
            }
            v1 = bid_values[bid1]
            v2 = bid_values[bid2]
            if v1 > v2:
                return {"outcome_p1_high": 寿0.5, "outcome_p1_high_alt": 0.5}
            elif v2 > v1:
                return {"outcome_p2_high": 0.5, "outcome_p2_high_alt": 0.5}
            else:
                return {"tie_p1_wins": 0.5, "tie_p2_wins": 0.5}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            if next_state.startswith("outcome_p1"):
                return "winner_player_1"
            elif next_state.startswith("outcome_p2"):
                return "winner_player_2"
            else:
                return "tie"
        return "game_over"

    def reward(self, state, joint_action, next_state, player):
        if state != "s0":
            return 0.0
        bid_values = {
            "low_bid": 1.0,
            "medium_bid": 2.0,
            "high_bid": 3.0
        }
        value_p1 = 3.0
        value_p2 = 3.0
        bid1 = bid_values[joint_action["player_1"]]
        bid2 = bid_values[joint_action["player_2"]]
        if player == "player_1":
            if next_state.startswith("outcome_p1"):
                return value_p1 - bid1
            else:
                return 0.0
        else:
            if next_state.startswith("outcome_p2"):
                return value_p2 - bid2
            else:
                return 0.0

    def is_terminal(self, state):
        return state == "terminal" or state.startswith("outcome") or state.startswith("tie")
