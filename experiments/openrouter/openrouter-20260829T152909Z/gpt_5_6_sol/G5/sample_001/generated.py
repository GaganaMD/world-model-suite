class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if player not in self.players:
            raise ValueError("Unknown player")
        if self.is_terminal(state):
            return []
        if state == "s0":
            return ["heads", "tails"]
        raise ValueError("Unknown state")

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        if state != "s0":
            raise ValueError("Unknown state")

        player_1_action = joint_action["player_1"]
        player_2_action = joint_action["player_2"]

        if player_1_action == "heads" and player_2_action == "heads":
            return {"terminal_heads_heads": 1.0}
        if player_1_action == "heads" and player_2_action == "tails":
            return {"terminal_heads_tails": 1.0}
        if player_1_action == "tails" and player_2_action == "heads":
            return {"terminal_tails_heads": 1.0}
        if player_1_action == "tails" and player_2_action == "tails":
            return {"terminal_tails_tails": 1.0}
        raise ValueError("Invalid joint action")

    def observation(self, state, joint_action, next_state, player):
        if player not in self.players:
            raise ValueError("Unknown player")
        if next_state == "terminal_heads_heads":
            return ("revealed", "heads", "heads")
        if next_state == "terminal_heads_tails":
            return ("revealed", "heads", "tails")
        if next_state == "terminal_tails_heads":
            return ("revealed", "tails", "heads")
        if next_state == "terminal_tails_tails":
            return ("revealed", "tails", "tails")
        return "coins_hidden"

    def reward(self, state, joint_action, next_state, player):
        if player not in self.players:
            raise ValueError("Unknown player")
        if not self.is_terminal(next_state):
            return 0.0

        matching = next_state in (
            "terminal_heads_heads",
            "terminal_tails_tails",
        )
        if player == "player_1":
            return 1.0 if matching else -1.0
        return -1.0 if matching else 1.0

    def is_terminal(self, state):
        return state in (
            "terminal_heads_heads",
            "terminal_heads_tails",
            "terminal_tails_heads",
            "terminal_tails_tails",
        )