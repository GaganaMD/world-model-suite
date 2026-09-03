class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["safe_route", "risky_route"]
    def transition(self, state, joint_action):
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action
        if state in {"goal", "collision"}:
            return {state: 1.0}
        if state == "s0":
            if action == "safe_route":
                return {"s1": 1.0}
            if action == "risky_route":
                return {"goal": 0.7, "collision": 0.3}
        if state == "s1":
            if action == "safe_route":
                return {"s2": 1.0}
            if action == "risky_route":
                return {"goal": 0.8, "collision": 0.2}
        if state == "s2":
            if action == "safe_route":
                return {"goal": 1.0}
            if action == "risky_route":
                return {"goal": 0.9, "collision": 0.1}
        return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player):
        if next_state == "goal":
            return 10.0
        if next_state == "collision":
            return -10.0
        return -1.0
    def is_terminal(self, state): return state in {"goal", "collision"}
    def state_features(self, state):
        if state == "goal":
            return {"location": "destination", "goal_reached": True, "collision": False}
        if state == "collision":
            return {"location": "route", "goal_reached": False, "collision": True}
        return {"location": "route", "goal_reached": False, "collision": False}