class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["kicker", "goalkeeper"]

    def initial_state(self):
        return "initial"

    def legal_actions(self, state, player):
        if state == "initial":
            return ["left", "center", "right"]
        return []

    def transition(self, state, joint_action):
        if state == "initial":
            return {"terminal": 1.0}
        return {}

    def observation(self, state, joint_action, next_state, player):
        kicker_action = joint_action["kicker"]
        goalkeeper_action = joint_action["goalkeeper"]
        goal = kicker_action != goalkeeper_action
        return "goal" if goal else "save"

    def reward(self, state, joint_action, next_state, player):
        kicker_action = joint_action["kicker"]
        goalkeeper_action = joint_action["goalkeeper"]
        goal = kicker_action != goalkeeper_action
        if player == "kicker":
            return 1.0 if goal else -1.0
        else:  # goalkeeper
            return -1.0 if goal else 1.0

    def is_terminal(self, state):
        return state == "terminal"