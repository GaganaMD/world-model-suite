class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["roll"]

    def transition(self, state, joint_action):
        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]
        outcomes = {}
        if state == "s0" and action_1 == "roll" and action_2 == "roll":
            for die_1 in range(1, 7):
                for die_2 in range(1, 7):
                    outcomes[f"terminal_{die_1}_{die_2}"] = 1.0 / 36.0
            return outcomes
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state.startswith("terminal_"):
            parts = next_state.split("_")
            die_1 = parts[1]
            die_2 = parts[2]
            if die_1 > die_2:
                result = "player_1_wins"
            elif die_2 > die_1:
                result = "player_2_wins"
            else:
                result = "tie"
            return f"player_1_rolled_{die_1}_player_2_rolled_{die_2}_{result}"
        return "round_complete"

    def reward(self, state, joint_action, next_state, player):
        if next_state.startswith("terminal_"):
            parts = next_state.split("_")
            die_1 = int(parts[1])
            die_2 = int(parts[2])
            if die_1 == die_2:
                return 0.0
            if player == "player_1":
                return 1.0 if die_1 > die_2 else -1.0
            return 1.0 if die_2 > die_1 else -1.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal" or state.startswith("terminal_")
