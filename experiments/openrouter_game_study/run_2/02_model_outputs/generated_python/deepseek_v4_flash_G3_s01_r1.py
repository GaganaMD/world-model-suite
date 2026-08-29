class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            return {
                "s1_heads": 0.5,
                "s1_tails": 0.5
            }
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            return f"preflip_{player}"
        if next_state == "s1_heads":
            return f"coin_heads_{player}"
        if next_state == "s1_tails":
            return f"coin_tails_{player}"
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            coin = "heads" if next_state == "s1_heads" else "tails"
            p1_match = (p1 == coin)
            p2_match = (p2 == coin)
            if p1_match and p2_match:
                return 0.0
            if p1_match and not p2_match:
                return 1.0 if player == "player_1" else -1.0
            if p2_match and not p1_match:
                return -1.0 if player == "player_1" else 1.0
            return 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
