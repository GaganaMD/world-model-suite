class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player in ("player_1", "player_2"):
            return ["roll"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        player_1_action = joint_action["player_1"]
        player_2_action = joint_action["player_2"]

        if player_1_action == "roll" and player_2_action == "roll":
            outcomes = {}
            probability = 1.0 / 36.0
            for player_1_roll in range(1, 7):
                for player_2_roll in range(1, 7):
                    if player_1_roll == 6 and player_2_roll == 6:
                        outcomes[("terminal", player_1_roll, player_2_roll)] = (
                            1.0 - sum(outcomes.values())
                        )
                    else:
                        outcomes[("terminal", player_1_roll, player_2_roll)] = probability
            return outcomes

        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if self.is_terminal(next_state):
            player_1_roll = next_state[1]
            player_2_roll = next_state[2]
            if player == "player_1":
                return ("roll_result", player_1_roll, player_2_roll)
            if player == "player_2":
                return ("roll_result", player_2_roll, player_1_roll)
        return "waiting"

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state) or not self.is_terminal(next_state):
            return 0.0

        player_1_roll = next_state[1]
        player_2_roll = next_state[2]

        if player_1_roll == player_2_roll:
            return 0.0
        if player == "player_1":
            return 1.0 if player_1_roll > player_2_roll else -1.0
        if player == "player_2":
            return 1.0 if player_2_roll > player_1_roll else -1.0
        return 0.0

    def is_terminal(self, state):
        return (
            isinstance(state, tuple)
            and len(state) == 3
            and state[0] == "terminal"
        )