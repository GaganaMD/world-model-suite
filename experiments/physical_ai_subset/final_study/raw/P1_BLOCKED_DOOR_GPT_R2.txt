class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "left_closed"
    def legal_actions(self, state, player): return ["move_left", "move_right", "open_door"]
    def transition(self, state, joint_action):
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action
        if state == "left_closed":
            return {"left_open": 1.0} if action == "open_door" else {"left_closed": 1.0}
        if state == "left_open":
            return {"goal": 1.0} if action == "move_right" else {"left_open": 1.0}
        return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player): return 1.0 if next_state == "goal" and state != "goal" else 0.0
    def is_terminal(self, state): return state == "goal"
    def state_features(self, state):
        return {"door_open": state in {"left_open", "goal"}, "goal_reached": state == "goal", "location": "goal" if state == "goal" else "left"}