class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "deal"

    def legal_actions(self, state, player):
        if player not in self.players:
            return []
        if state == "deal":
            return ["continue"]
        if isinstance(state, tuple) and state[0] == "bidding":
            return ["bid_0", "bid_1", "bid_2"]
        return []

    def transition(self, state, joint_action):
        if state == "deal":
            return {
                ("bidding", "low", "low"): 0.25,
                ("bidding", "low", "high"): 0.25,
                ("bidding", "high", "low"): 0.25,
                ("bidding", "high", "high"): 0.25,
            }

        if isinstance(state, tuple) and state[0] == "bidding":
            value_1 = state[1]
            value_2 = state[2]
            action_1 = joint_action["player_1"]
            action_2 = joint_action["player_2"]

            bid_1 = 0 if action_1 == "bid_0" else 1 if action_1 == "bid_1" else 2
            bid_2 = 0 if action_2 == "bid_0" else 1 if action_2 == "bid_1" else 2

            if bid_1 > bid_2:
                return {
                    ("terminal", value_1, value_2, bid_1, bid_2, "player_1"): 1.0
                }
            if bid_2 > bid_1:
                return {
                    ("terminal", value_1, value_2, bid_1, bid_2, "player_2"): 1.0
                }
            return {
                ("terminal", value_1, value_2, bid_1, bid_2, "player_1"): 0.5,
                ("terminal", value_1, value_2, bid_1, bid_2, "player_2"): 0.5,
            }

        if self.is_terminal(state):
            return {state: 1.0}

        return {"deal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if player not in self.players:
            return "invalid_player"

        if isinstance(next_state, tuple) and next_state[0] == "bidding":
            own_value = next_state[1] if player == "player_1" else next_state[2]
            return ("private_value", own_value)

        if isinstance(next_state, tuple) and next_state[0] == "terminal":
            own_value = next_state[1] if player == "player_1" else next_state[2]
            own_bid = next_state[3] if player == "player_1" else next_state[4]
            winning_bid = max(next_state[3], next_state[4])
            outcome = "win" if next_state[5] == player else "lose"
            return ("auction_result", own_value, own_bid, winning_bid, outcome)

        return "waiting"

    def reward(self, state, joint_action, next_state, player):
        if player not in self.players:
            return 0.0

        if not (isinstance(next_state, tuple) and next_state[0] == "terminal"):
            return 0.0

        winner = next_state[5]
        if winner != player:
            return 0.0

        if player == "player_1":
            value = 1 if next_state[1] == "low" else 2
            bid = next_state[3]
        else:
            value = 1 if next_state[2] == "low" else 2
            bid = next_state[4]

        return float(value - bid)

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) > 0 and state[0] == "terminal"