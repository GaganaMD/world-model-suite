class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["rock", "paper", "scissors"]
        return []

    def transition(self, state, joint_action):
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return "round_played"

    def reward(self, state, joint_action, next_state, player):
        action = joint_action[player]
        opponent = "player_2" if player == "player_1" else "player_1"
        opponent_action = joint_action[opponent]

        if action == opponent_action:
            return 0.0

        if (
            (action == "rock" and opponent_action == "scissors")
            or (action == "scissors" and opponent_action == "paper")
            or (action == "paper" and opponent_action == "rock")
        ):
            return 1.0

        return -1.0

    def is_terminal(self, state):
        return state == "terminal"