class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "start_charged"
    def legal_actions(self, state, player):
        if state in {"delivered", "failed"}: return []
        if state == "start_charged": return ["move"]
        if state == "start_empty": return ["charge"]
        if state == "destination_charged": return ["deliver", "move"]
        return ["charge"]
    def transition(self, state, joint_action):
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action
        if state == "start_charged" and action == "move": return {"destination_empty": 0.8, "failed": 0.2}
        if state == "start_empty" and action == "charge": return {"start_charged": 1.0}
        if state == "destination_charged" and action == "deliver": return {"delivered": 1.0}
        if state == "destination_charged" and action == "move": return {"start_empty": 0.8, "failed": 0.2}
        if state == "destination_empty" and action == "charge": return {"destination_charged": 1.0}
        if state in {"delivered", "failed"}: return {state: 1.0}
        return {"failed": 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player):
        if next_state == "delivered": return 10.0
        if next_state == "failed": return -10.0
        return -1.0
    def is_terminal(self, state): return state in {"delivered", "failed"}
    def state_features(self, state):
        features = {
            "start_charged": {"battery": 1, "failed": False, "location": "start", "package_delivered": False},
            "start_empty": {"battery": 0, "failed": False, "location": "start", "package_delivered": False},
            "destination_charged": {"battery": 1, "failed": False, "location": "destination", "package_delivered": False},
            "destination_empty": {"battery": 0, "failed": False, "location": "destination", "package_delivered": False},
            "delivered": {"battery": 0, "failed": False, "location": "destination", "package_delivered": True},
            "failed": {"battery": 0, "failed": True, "location": "route", "package_delivered": False}
        }
        return features[state]