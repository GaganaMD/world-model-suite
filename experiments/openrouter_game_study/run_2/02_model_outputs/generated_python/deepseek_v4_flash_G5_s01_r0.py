class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        # Terminal state has no legal actions (but contract requires non-empty for non-terminal only)
        return ["heads", "tails"]  # Should not be called in terminal

    def transition(self, state, joint_action):
        if state == "s0":
            # Deterministic transition to terminal after both choose
            return {"terminal": 1.0}
        # If somehow called in terminal, stay terminal
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # In this simultaneous-move game, no private info; return empty observation
        return ""

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == a2:
                # Same face: Player 1 wins both pennies (reward +1 for P1, -1 for P2)
                return 1.0 if player == "player_1" else -1.0
            else:
                # Different: Player 2 wins both pennies
                return -1.0 if player == "player_1" else 1.0
        # Terminal state: no reward
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
