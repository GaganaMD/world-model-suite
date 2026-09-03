class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): return ["safe_route", "risky_route"]
    def transition(self, state, joint_action): 
        if joint_action == "safe_route":
            if state == "start":
                return {"midpoint": 1.0}
            elif state == "midpoint":
                return {"goal": 1.0}
        elif joint_action == "risky_route":
            if state == "start":
                return {"goal": 0.8, "collision": 0.2}
        return {}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "collision":
            return -1.0
        elif next_state == "goal":
            return 1.0
        return 0.0
    def is_terminal(self, state): return state in {"goal", "collision"}
    def state_features(self, state): 
        if state == "start":
            return {"location": "start", "goal_reached": False, "collision": False}
        elif state == "midpoint":
            return {"location": "midpoint", "goal_reached": False, "collision": False}
        elif state == "goal":
            return {"location": "goal", "goal_reached": True, "collision": False}
        elif state == "collision":
            return {"location": "collision", "goal_reached": False, "collision": True}