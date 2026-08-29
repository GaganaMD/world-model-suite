class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["stay_silent", "testify"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            return f"state={state};player={player};action={joint_action.get(player, 'unknown')}"
        return f"state={state};player={player};action={joint_action.get(player, 'unknown')}"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            a1 = joint_action.get("player_1", "stay_silent")
            a2 = joint_action.get("player_2", "stay_silent")
            if player == "player_1":
                if a1 == "stay_silent" and a2 == "stay_silent":
                    return -1.0
                if a1 == "testify" and a2 == "testify":
                    return -3.0
                if a1 == "testify" and a2 == "stay_silent":
                    return 0.0
                if a1 == "stay_silent" and a2 == "testify":
                    return -5.0
            else:
                if a1 == "stay_silent" and a2 == "stay_silent":
                    return -1.0
                if a1 == "testify" and a2 == "testify":
                    return -3.0
                if a1 == "stay_silent" and a2 == "testify":
                    return 0.0
                if a1 == "testify" and a2 == "stay_silent":
                    return -5.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
