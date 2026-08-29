class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["kicker", "goalkeeper"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if player == "kicker":
            return ["left", "center", "right"]
        elif player == "goalkeeper":
            return ["left", "center", "right"]
    def transition(self, state, joint_action): 
        kicker_action = joint_action["kicker"]
        goalkeeper_action = joint_action["goalkeeper"]
        if kicker_action == goalkeeper_action:
            return {"miss": 1.0}
        else:
            return {"goal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if player == "kicker":
            return f"kick {joint_action['kicker']}"
        elif player == "goalkeeper":
            return f"dive {joint_action['goalkeeper']}"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "goal" and player == "kicker":
            return 1.0
        elif next_state == "goal" and player == "goalkeeper":
            return -1.0
        elif next_state == "miss" and player == "kicker":
            return -1.0
        elif next_state == "miss" and player == "goalkeeper":
            return 1.0
    def is_terminal(self, state): 
        return state in ["goal", "miss"]