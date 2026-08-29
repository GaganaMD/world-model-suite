class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["kicker", "goalkeeper"]

    def initial_state(self):
        return "penalty"

    def legal_actions(self, state, player):
        if state == "penalty":
            return ["left", "center", "right"]
        return []

    def transition(self, state, joint_action):
        if state == "penalty":
            kicker_action = joint_action["kicker"]
            keeper_action = joint_action["goalkeeper"]
            if kicker_action == keeper_action:
                return {"saved": 1.0}
            else:
                return {"goal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "penalty":
            return f"penalty_{next_state}"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state == "penalty":
            if next_state == "goal":
                if player == "kicker":
                    return 1.0
                else:
                    return -1.0
            else:  # saved
                if player == "kicker":
                    return -1.0
                else:
                    return 1.0
        return 0.0

    def is_terminal(self, state):
        return state in ["goal", "saved", "terminal"]
