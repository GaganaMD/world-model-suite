class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            p1_action = joint_action.get("player_1", "unknown")
            p2_action = joint_action.get("player_2", "unknown")
            if player == "player_1":
                return f"p1={p1_action},p2={p2_action}"
            else:
                return f"p1={p1_action},p2={p2_action}"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            p1_action = joint_action.get("player_1", "")
            p2_action = joint_action.get("player_2", "")
            if p1_action == p2_action:
                # Player 1 keeps both coins: +1 for P1, -1 for P2
                if player == "player_1":
                    return 1.0
                else:
                    return -1.0
            else:
                # Player 2 keeps both coins: -1 for P1, +1 for P2
                if player == "player_1":
                    return -1.0
                else:
                    return 1.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
