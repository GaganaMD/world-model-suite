class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player):
        if player != "robot" or self.is_terminal(state):
            return []
        return ["safe_route", "risky_route"]
    def transition(self, state, joint_action):
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action
        if self.is_terminal(state):
            return {state: 1.0}
        if state == "start":
            if action == "safe_route":
                return {"safe_midpoint": 1.0}
            if action == "risky_route":
                return {"goal": 0.7, "collision": 0.3}
        if state == "safe_midpoint":
            if action == "safe_route":
                return {"goal": 1.0}
            if action == "risky_route":
                return {"goal": 0.8, "collision": 0.2}
        return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player):
        if next_state == "goal":
            return 1.0
        if next_state == "collision":
            return -1.0
        return -0.1
    def is_terminal(self, state): return state in {"goal", "collision"}
    def state_features(self, state):
        if state == "goal":
            return {"location": "destination", "goal_reached": True, "collision": False}
        if state == "collision":
            return {"location": "collision_site", "goal_reached": False, "collision": True}
        if state == "safe_midpoint":
            return {"location": "safe_route", "goal_reached": False, "collision": False}
        return {"location": "start", "goal_reached": False, "collision": False}