class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): return ["safe_route", "risky_route"] if state == "start" and player == "robot" else []
    def transition(self, state, joint_action):
        if state != "start": return {state: 1.0}
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action[0] if isinstance(joint_action, (list, tuple)) else joint_action
        if action == "safe_route": return {"goal": 1.0}
        if action == "risky_route": return {"goal": 0.7, "collision": 0.3}
        return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player): return 1.0 if next_state == "goal" else -1.0 if next_state == "collision" else 0.0
    def is_terminal(self, state): return state in {"goal", "collision"}
    def state_features(self, state): return {"location": "destination" if state == "goal" else "collision_site" if state == "collision" else "start", "goal_reached": state == "goal", "collision": state == "collision"}