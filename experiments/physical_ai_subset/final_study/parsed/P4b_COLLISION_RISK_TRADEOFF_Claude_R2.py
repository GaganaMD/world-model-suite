class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "start"

    def legal_actions(self, state, player):
        if player != "robot":
            return []
        if self.is_terminal(state):
            return []
        return ["safe_route", "risky_route"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action
        if action not in ("safe_route", "risky_route"):
            return {state: 1.0}
        if state == "start":
            if action == "safe_route":
                return {"safe_mid": 1.0}
            return {"risky_mid": 0.75, "collision": 0.25}
        if state == "safe_mid":
            if action == "safe_route":
                return {"safe_near_goal": 1.0}
            return {"risky_mid": 0.7, "collision": 0.3}
        if state == "safe_near_goal":
            if action == "safe_route":
                return {"goal": 1.0}
            return {"goal": 0.8, "collision": 0.2}
        if state == "risky_mid":
            if action == "safe_route":
                return {"safe_near_goal": 1.0}
            return {"goal": 0.7, "collision": 0.3}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        features = self.state_features(next_state)
        if features["collision"]:
            return "obs_collision"
        if features["goal_reached"]:
            return "obs_goal"
        return "obs_" + features["location"]

    def reward(self, state, joint_action, next_state, player):
        if player != "robot":
            return 0.0
        features = self.state_features(next_state)
        if features["collision"]:
            return -20.0
        if features["goal_reached"]:
            return 10.0
        return -1.0

    def is_terminal(self, state):
        return state in {"goal", "collision"}

    def state_features(self, state):
        if state == "goal":
            return {"location": "destination", "goal_reached": True, "collision": False}
        if state == "collision":
            return {"location": "risky_route", "goal_reached": False, "collision": True}
        if state == "safe_mid":
            return {"location": "safe_route", "goal_reached": False, "collision": False}
        if state == "safe_near_goal":
            return {"location": "near_destination", "goal_reached": False, "collision": False}
        if state == "risky_mid":
            return {"location": "risky_route", "goal_reached": False, "collision": False}
        return {"location": "start", "goal_reached": False, "collision": False}