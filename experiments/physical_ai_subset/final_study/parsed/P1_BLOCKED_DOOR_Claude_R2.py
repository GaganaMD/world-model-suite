class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "left_closed"

    def legal_actions(self, state, player):
        if player != "robot":
            return []
        if self.is_terminal(state):
            return []
        return ["move_left", "move_right", "open_door"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action
        if action not in ("move_left", "move_right", "open_door"):
            return {state: 1.0}
        if state == "left_closed":
            if action == "move_left":
                return {"left_closed": 1.0}
            if action == "move_right":
                return {"left_closed": 0.9, "doorway_closed": 0.1}
            return {"left_open": 0.8, "left_closed": 0.2}
        if state == "left_open":
            if action == "move_left":
                return {"left_open": 1.0}
            if action == "move_right":
                return {"doorway_open": 0.9, "left_open": 0.1}
            return {"left_open": 1.0}
        if state == "doorway_closed":
            if action == "move_left":
                return {"left_closed": 1.0}
            if action == "move_right":
                return {"doorway_closed": 1.0}
            return {"doorway_open": 0.8, "doorway_closed": 0.2}
        if state == "doorway_open":
            if action == "move_left":
                return {"left_open": 1.0}
            if action == "move_right":
                return {"goal": 0.95, "doorway_open": 0.05}
            return {"doorway_open": 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        features = self.state_features(next_state)
        return "loc=" + features["location"] + ";door_open=" + str(features["door_open"]) + ";goal=" + str(features["goal_reached"])

    def reward(self, state, joint_action, next_state, player):
        if player != "robot":
            return 0.0
        if self.is_terminal(state):
            return 0.0
        reward = -1.0
        if next_state == "goal":
            reward += 20.0
        if state in ("left_closed", "doorway_closed") and next_state in ("left_open", "doorway_open"):
            reward += 2.0
        return reward

    def is_terminal(self, state):
        return state in {"goal"}

    def state_features(self, state):
        table = {
            "left_closed": {"location": "left", "goal_reached": False, "door_open": False},
            "left_open": {"location": "left", "goal_reached": False, "door_open": True},
            "doorway_closed": {"location": "doorway", "goal_reached": False, "door_open": False},
            "doorway_open": {"location": "doorway", "goal_reached": False, "door_open": True},
            "goal": {"location": "right", "goal_reached": True, "door_open": True},
        }
        return dict(table.get(state, {"location": "left", "goal_reached": False, "door_open": False}))