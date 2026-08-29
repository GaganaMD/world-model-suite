class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return ("auction", "low", "high")

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player not in ("player_1", "player_2"):
            return []
        return ["bid_0", "bid_10", "bid_20"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        bid1 = joint_action["player_1"]
        bid2 = joint_action["player_2"]

        if bid1 == "bid_0":
            amount1 = 0.0
        elif bid1 == "bid_10":
            amount1 = 10.0
        elif bid1 == "bid_20":
            amount1 = 20.0
        else:
            amount1 = 0.0

        if bid2 == "bid_0":
            amount2 = 0.0
        elif bid2 == "bid_10":
            amount2 = 10.0
        elif bid2 == "bid_20":
            amount2 = 20.0
        else:
            amount2 = 0.0

        if amount1 > amount2:
            return {"terminal_player_1": 1.0}
        if amount2 > amount1:
            return {"terminal_player_2": 1.0}
        return {"terminal_player_1": 0.5, "terminal_player_2": 0.5}

    def observation(self, state, joint_action, next_state, player):
        if player not in ("player_1", "player_2"):
            return "own_value=low;own_bid=unknown;winner=none"

        if isinstance(state, tuple) and len(state) >= 3 and state[0] == "auction":
            own_value = state[1] if player == "player_1" else state[2]
        else:
            own_value = "low"

        own_bid = str(joint_action[player])
        own_value = str(own_value)

        if next_state == "terminal_player_1":
            winner = "player_1"
        elif next_state == "terminal_player_2":
            winner = "player_2"
        else:
            winner = "none"

        return "own_value=" + own_value + ";own_bid=" + own_bid + ";winner=" + winner

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal_player_1" and player != "player_1":
            return 0.0
        if next_state == "terminal_player_2" and player != "player_2":
            return 0.0
        if next_state != "terminal_player_1" and next_state != "terminal_player_2":
            return 0.0

        if player not in ("player_1", "player_2"):
            return 0.0

        if isinstance(state, tuple) and len(state) >= 3 and state[0] == "auction":
            own_value = state[1] if player == "player_1" else state[2]
        else:
            own_value = "low"

        value = 20.0 if own_value == "high" else 10.0

        bid = str(joint_action[player])
        if bid == "bid_0":
            amount = 0.0
        elif bid == "bid_10":
            amount = 10.0
        elif bid == "bid_20":
            amount = 20.0
        else:
            amount = 0.0

        return value - amount

    def is_terminal(self, state):
        return state == "terminal_player_1" or state == "terminal_player_2"