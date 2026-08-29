class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        return []

    def transition(self, state, joint_action):
        if state == "s0":
            # Fair coin flip: heads or tails with equal probability
            return {"terminal_heads": 0.5, "terminal_tails": 0.5}
        # Terminal states have no transitions
        return {}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal_heads":
            return "heads"
        elif next_state == "terminal_tails":
            return "tails"
        return ""

    def reward(self, state, joint_action, next_state, player):
        if state != "s0":
            return 0.0
        # Determine coin result from next_state
        coin = "heads" if next_state == "terminal_heads" else "tails"
        # Get player's call
        call = joint_action[player]
        # Determine if this player matches
        player_matches = (call == coin)
        # Determine if the other player matches
        other = "player_2" if player == "player_1" else "player_1"
        other_matches = (joint_action[other] == coin)
        # Exactly one match: winner gets +1, loser gets -1; otherwise draw (0)
        if player_matches and not other_matches:
            return 1.0
        elif not player_matches and other_matches:
            return -1.0
        else:
            return 0.0

    def is_terminal(self, state):
        return state in ("terminal_heads", "terminal_tails")