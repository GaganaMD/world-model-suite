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
            a1 = joint_action.get("player_1", "unknown")
            a2 = joint_action.get("player_2", "unknown")
            if player == "player_1":
                return f"obs_p1: my_choice={a1}, opponent_choice={a2}"
            else:
                return f"obs_p2: my_choice={a2}, opponent_choice={a1}"
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action.get("player_1", "unknown")
            a2 = joint_action.get("player_2", "unknown")
            if a1 == a2:
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
