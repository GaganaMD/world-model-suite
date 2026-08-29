class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["rock", "paper", "scissors"]

    def transition(self, state, joint_action):
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return f"player_1:{joint_action['player_1']};player_2:{joint_action['player_2']}"

    def reward(self, state, joint_action, next_state, player):
        first = joint_action["player_1"]
        second = joint_action["player_2"]
        if first == second:
            return 0.0
        first_wins = (
            (first == "rock" and second == "scissors")
            or (first == "paper" and second == "rock")
            or (first == "scissors" and second == "paper")
        )
        if player == "player_1":
            return 1.0 if first_wins else -1.0
        return -1.0 if first_wins else 1.0

    def is_terminal(self, state):
        return state == "terminal"
