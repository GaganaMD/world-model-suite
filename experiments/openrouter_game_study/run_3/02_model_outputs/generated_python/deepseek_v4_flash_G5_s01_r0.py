class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        # Terminal state has no legal actions
        return []

    def transition(self, state, joint_action):
        if state == "s0":
            # Both players choose simultaneously; outcome is deterministic
            return {"terminal": 1.0}
        # Terminal state is absorbing
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            # In the initial state, players observe nothing (or a dummy observation)
            return "no_obs"
        # Terminal state observation
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == a2:
                # Same face: Player 1 wins both pennies
                if player == "player_1":
                    return 2  # Player 1 gets both coins (value 2)
                else:
                    return 0
            else:
                # Different faces: Player 2 wins both pennies
                if player == "player_2":
                    return 2
                else:
                    return 0
        # Terminal state: no further reward
        return 0

    def is_terminal(self, state):
        return state == "terminal"
