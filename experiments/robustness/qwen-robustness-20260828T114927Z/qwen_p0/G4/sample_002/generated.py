class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["kicker", "goalkeeper"]
    def initial_state(self): return ("s0", "left")
    def legal_actions(self, state, player):
        if player == "kicker":
            return ["left", "center", "right"]
        elif player == "goalkeeper":
            return ["left", "right", "stay_center"]
    def transition(self, state, joint_action):
        kicker_action, goalkeeper_action = joint_action["kicker"], joint_action["goalkeeper"]
        if kicker_action == goalkeeper_action:
            return {"terminal": 1.0}
        else:
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if player == "kicker":
            return f"Kicker {kicker_action}"
        elif player == "goalkeeper":
            return f"Goalkeeper {goalkeeper_action}"
    def reward(self, state, joint_action, next_state, player):
        kicker_action, goalkeeper_action = joint_action["kicker"], joint_action["goalkeeper"]
        if kicker_action == goalkeeper_action:
            return -1.0
        else:
            return 1.0
    def is_terminal(self, state): return state[0] == "terminal"