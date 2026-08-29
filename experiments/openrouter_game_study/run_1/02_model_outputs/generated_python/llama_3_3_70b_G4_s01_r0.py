class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["kicker", "goalkeeper"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if player == "kicker": 
            return ["left", "center", "right"]
        else: 
            return ["left", "center", "right"]
    def transition(self, state, joint_action): 
        kicker_action = joint_action["kicker"]
        goalkeeper_action = joint_action["goalkeeper"]
        if kicker_action == goalkeeper_action: 
            return {"goal": 0.0, "no_goal": 1.0}
        else: 
            return {"goal": 1.0, "no_goal": 0.0}
    def observation(self, state, joint_action, next_state, player): 
        kicker_action = joint_action["kicker"]
        goalkeeper_action = joint_action["goalkeeper"]
        if next_state == "goal": 
            return f"scored_{kicker_action}_{goalkeeper_action}"
        else: 
            return f"missed_{kicker_action}_{goalkeeper_action}"
    def reward(self, state, joint_action, next_state, player): 
        if player == "kicker" and next_state == "goal": 
            return 1.0
        elif player == "goalkeeper" and next_state == "no_goal": 
            return 1.0
        else: 
            return 0.0
    def is_terminal(self, state): 
        return state in ["goal", "no_goal"]
