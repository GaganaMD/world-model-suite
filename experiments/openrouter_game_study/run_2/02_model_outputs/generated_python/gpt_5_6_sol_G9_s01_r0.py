class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["0-3", "1-2", "2-1", "3-0"]

    def transition(self, state, joint_action):
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        first_1 = int(joint_action["player_1"][0])
        first_2 = int(joint_action["player_2"][0])
        wins_1 = (1 if first_1 > first_2 else 0) + (1 if 3 - first_1 > 3 - first_2 else 0)
        wins_2 = (1 if first_2 > first_1 else 0) + (1 if 3 - first_2 > 3 - first_1 else 0)
        outcome = "win" if (player == "player_1" and wins_1 > wins_2) or (player == "player_2" and wins_2 > wins_1) else "loss" if wins_1 != wins_2 else "draw"
        return f"{joint_action['player_1']}|{joint_action['player_2']}|{outcome}"

    def reward(self, state, joint_action, next_state, player):
        first_1 = int(joint_action["player_1"][0])
        first_2 = int(joint_action["player_2"][0])
        wins_1 = (1 if first_1 > first_2 else 0) + (1 if 3 - first_1 > 3 - first_2 else 0)
        wins_2 = (1 if first_2 > first_1 else 0) + (1 if 3 - first_2 > 3 - first_1 else 0)
        if wins_1 == wins_2:
            return 0.0
        if player == "player_1":
            return 1.0 if wins_1 > wins_2 else -1.0
        return 1.0 if wins_2 > wins_1 else -1.0

    def is_terminal(self, state):
        return state == "terminal"
