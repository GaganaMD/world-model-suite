class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "start_b1"
    def legal_actions(self, state, player):
        if state == "start_b1": return ["move", "charge"]
        if state == "start_b2": return ["move"]
        if state in {"destination_b1", "destination_b2"}: return ["deliver"]
        return []
    def transition(self, state, joint_action):
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        if state == "start_b1" and action == "move": return {"destination_b1": 0.8, "failed": 0.2}
        if state == "start_b1" and action == "charge": return {"start_b2": 1.0}
        if state == "start_b2" and action == "move": return {"destination_b1": 0.9, "destination_b2": 0.1}
        if state in {"destination_b1", "destination_b2"} and action == "deliver": return {"delivered": 1.0}
        return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player):
        if next_state == "delivered": return 10.0
        if next_state == "failed": return -10.0
        return -1.0
    def is_terminal(self, state): return state in {"delivered", "failed"}
    def state_features(self, state):
        features = {
            "start_b1": {"battery": 1, "failed": False, "location": "start", "package_delivered": False},
            "start_b2": {"battery": 2, "failed": False, "location": "start", "package_delivered": False},
            "destination_b1": {"battery": 1, "failed": False, "location": "destination", "package_delivered": False},
            "destination_b2": {"battery": 2, "failed": False, "location": "destination", "package_delivered": False},
            "delivered": {"battery": 0, "failed": False, "location": "destination", "package_delivered": True},
            "failed": {"battery": 0, "failed": True, "location": "route", "package_delivered": False}
        }
        return features[state]