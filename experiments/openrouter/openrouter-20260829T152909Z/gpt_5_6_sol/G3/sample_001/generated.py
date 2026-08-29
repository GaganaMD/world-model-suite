class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "awaiting_calls"

    def legal_actions(self, state, player):
        if state == "awaiting_calls" and player in self.players:
            return ["heads", "tails"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        player_1_call = joint_action["player_1"]
        player_2_call = joint_action["player_2"]

        heads_state = (
            "terminal",
            "heads",
            player_1_call,
            player_2_call,
        )
        tails_state = (
            "terminal",
            "tails",
            player_1_call,
            player_2_call,
        )
        return {heads_state: 0.5, tails_state: 0.5}

    def observation(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return "coin_not_flipped"

        result = next_state[1]
        player_call = next_state[2] if player == "player_1" else next_state[3]
        other_call = next_state[3] if player == "player_1" else next_state[2]

        if player_call == other_call:
            outcome = "draw"
        elif player_call == result:
            outcome = "win"
        else:
            outcome = "lose"

        return (result, player_call, outcome)

    def reward(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return 0.0

        result = next_state[1]
        player_1_call = next_state[2]
        player_2_call = next_state[3]

        if player_1_call == player_2_call:
            return 0.0

        player_call = player_1_call if player == "player_1" else player_2_call
        return 1.0 if player_call == result else -1.0

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 4 and state[0] == "terminal"