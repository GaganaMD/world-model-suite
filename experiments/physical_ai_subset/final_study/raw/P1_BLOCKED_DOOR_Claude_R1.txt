class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "left_closed"

    def legal_actions(self, state, player):
        return ["move_left", "move_right", "open_door"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        if state == "left_closed":
            if action == "move_left":
                return {"left_closed": 1.0}
            if action == "move_right":
                return {"left_closed": 1.0}
            if action == "open_door":
                return {"left_open": 0.9, "left_closed": 0.1}
        if state == "left_open":
            if action == "move_left":
                return {"left_open": 1.0}
            if action == "move_right":
                return {"doorway_open": 0.9, "left_open": 0.1}
            if action == "open_door":
                return {"left_open": 1.0}
        if state == "doorway_open":
            if action == "move_left":
                return {"left_open": 1.0}
            if action == "move_right":
                return {"goal": 0.9, "doorway_open": 0.1}
            if action == "open_door":
                return {"doorway_open": 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        features = self.state_features(next_state)
        return "loc=" + features["location"] + ";door_open=" + str(features["door_open"]) + ";goal=" + str(features["goal_reached"])

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        if next_state == "goal":
            return 10.0
        if state == "left_closed" and next_state == "left_open":
            return 1.0
        return -0.1

    def is_terminal(self, state):
        return state in {"goal"}

    def state_features(self, state):
        if state == "left_closed":
            return {"location": "left", "door_open": False, "goal_reached": False, "collision": False}
        if state == "left_open":
            return {"location": "left", "door_open": True, "goal_reached": False, "collision": False}
        if state == "doorway_open":
            return {"location": "doorway", "door_open": True, "goal_reached": False, "collision": False}
        if state == "goal":
            return {"location": "destination", "door_open": True, "goal_reached": True, "collision": False}
        return {"location": "left", "door_open": False, "goal_reached": False, "collision": False}