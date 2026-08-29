class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["roll"]

    def transition(self, state, joint_action):
        joint_action["player_1"]
        joint_action["player_2"]
        outcomes = {}
        for roll_1 in range(1, 7):
            for roll_2 in range(1, 7):
                outcomes[f"terminal_{roll_1}_{roll_2}"] = 1.0 / 36.0
        return outcomes

    def observation(self, state, joint_action, next_state, player):
        joint_action["player_1"]
        joint_action["player_2"]
        if next_state.startswith("terminal_"):
            parts = next_state.split("_")
            roll_1 = parts[1]
            roll_2 = parts[2]
            if player == "player_1":
                return f"your_roll={roll_1};opponent_roll={roll_2}"
            return f"your_roll={roll_2};opponent_roll={roll_1}"
        return "no_roll"

    def reward(self, state, joint_action, next_state, player):
        joint_action["player_1"]
        joint_action["player_2"]
        if not next_state.startswith("terminal_"):
            return 0.0
        parts = next_state.split("_")
        roll_1 = int(parts[1])
        roll_2 = int(parts[2])
        if roll_1 == roll_2:
            return 0.0
        if player == "player_1":
            return 1.0 if roll_1 > roll_2 else -1.0
        return 1.0 if roll_2 > roll_1 else -1.0

    def is_terminal(self, state):
        return state.startswith("terminal_")
