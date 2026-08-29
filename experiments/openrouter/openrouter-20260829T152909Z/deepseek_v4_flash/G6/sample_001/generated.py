class GeneratedPOSG(AbstractPOSG):
    def __init__(self):
        self.initial = "s0_1_2"  # player_1 value=1 (low), player_2 value=2 (high)
        self.terminal_p1 = "terminal_p1_wins"
        self.terminal_p2 = "terminal_p2_wins"

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return self.initial

    def legal_actions(self, state, player):
        if state.startswith("terminal"):
            return []
        return [0, 1, 2]  # possible bids

    def transition(self, state, joint_action):
        if state.startswith("terminal"):
            return {}
        bid1 = joint_action["player_1"]
        bid2 = joint_action["player_2"]
        if bid1 > bid2:
            return {self.terminal_p1: 1.0}
        elif bid1 < bid2:
            return {self.terminal_p2: 1.0}
        else:
            return {self.terminal_p1: 0.5, self.terminal_p2: 0.5}

    def observation(self, state, joint_action, next_state, player):
        if state.startswith("terminal"):
            return ""
        # state format: "s0_<value1>_<value2>"
        parts = state.split("_")
        value = int(parts[1]) if player == "player_1" else int(parts[2])
        return "low" if value == 1 else "high"

    def reward(self, state, joint_action, next_state, player):
        if state.startswith("terminal"):
            return 0.0
        parts = state.split("_")
        value = int(parts[1]) if player == "player_1" else int(parts[2])
        bid = joint_action[player]
        if (next_state == self.terminal_p1 and player == "player_1") or \
           (next_state == self.terminal_p2 and player == "player_2"):
            return float(value - bid)
        return 0.0

    def is_terminal(self, state):
        return state.startswith("terminal")