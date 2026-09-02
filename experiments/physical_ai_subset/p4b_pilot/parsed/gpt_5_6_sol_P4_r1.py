class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player):
        if player != "robot" or self.is_terminal(state):
            return []
        return ["safe_route", "risky_route"]
    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action[0] if isinstance(joint_action, (list, tuple)) else joint_action
        if action == "safe_route":
            return {"safe_progress": 1.0} if state == "s0" else {"goal": 1.0}
        if action == "risky_route":
            return {"goal": 0.75, "collision": 0.25}
        raise ValueError("Invalid action")
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player):
        if next_state == "goal":
            return 1.0
        if next_state == "collision":
            return -1.0
        return -0.1
    def is_terminal(self, state): return state in {"goal", "collision"}
    def state_features(self, state):
        locations = {"s0": "start", "safe_progress": "safe_route", "goal": "destination", "collision": "collision_site"}
        return {"location": locations.get(state, str(state)), "goal_reached": state == "goal", "collision": state == "collision"}