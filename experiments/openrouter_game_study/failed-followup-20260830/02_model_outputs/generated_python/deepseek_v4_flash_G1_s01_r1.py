class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["rock", "paper", "scissors"]
        if state == "terminal":
            return ["rock"]
        return ["rock", "paper", "scissors"]

    def transition(self, state, joint_action):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == a2:
                return {"s0": 1.0}
            else:
                return {"terminal": 1.0}
        if state == "terminal":
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            return f"obs_{a1}_{a2}_{next_state}"
        if state == "terminal":
            return "obs_terminal"
        return "obs_fallback"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 == a2:
                return 0.0
            if (a1 == "rock" and a2 == "scissors") or (a1 == "scissors" and a2 == "paper") or (a1 == "paper" and a2 == "rock"):
                if player == "player_1":
                    return 1.0
                else:
                    return -1.0
            else:
                if player == "player_1":
                    return -1.0
                else:
                    return 1.0
        if state == "terminal":
            return 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
