class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "ready"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player in self.players:
            return ["rock", "paper", "scissors"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        player_1_action = joint_action["player_1"]
        player_2_action = joint_action["player_2"]
        next_state = ("terminal", player_1_action, player_2_action)
        return {next_state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return "round_in_progress"

        player_1_action = joint_action["player_1"]
        player_2_action = joint_action["player_2"]

        if player == "player_1":
            own_action = player_1_action
            opponent_action = player_2_action
        else:
            own_action = player_2_action
            opponent_action = player_1_action

        if own_action == opponent_action:
            outcome = "draw"
        elif (
            (own_action == "rock" and opponent_action == "scissors")
            or (own_action == "paper" and opponent_action == "rock")
            or (own_action == "scissors" and opponent_action == "paper")
        ):
            outcome = "win"
        else:
            outcome = "loss"

        return (outcome, own_action, opponent_action)

    def reward(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return 0.0

        player_1_action = joint_action["player_1"]
        player_2_action = joint_action["player_2"]

        if player_1_action == player_2_action:
            return 0.0

        player_1_wins = (
            (player_1_action == "rock" and player_2_action == "scissors")
            or (player_1_action == "paper" and player_2_action == "rock")
            or (player_1_action == "scissors" and player_2_action == "paper")
        )

        if player == "player_1":
            return 1.0 if player_1_wins else -1.0
        return -1.0 if player_1_wins else 1.0

    def is_terminal(self, state):
        return (
            isinstance(state, tuple)
            and len(state) == 3
            and state[0] == "terminal"
        )