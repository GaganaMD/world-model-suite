class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "start_b2"

    def legal_actions(self, state, player):
        return ["move", "charge", "deliver"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        feats = self.state_features(state)
        location = feats["location"]
        battery = feats["battery"]
        if action == "move":
            if battery <= 0:
                return {"failed": 1.0}
            if location == "start":
                return {"mid_b" + str(battery - 1): 0.8, "start_b" + str(battery - 1): 0.2}
            if location == "mid":
                return {"dest_b" + str(battery - 1): 0.8, "mid_b" + str(battery - 1): 0.2}
            return {"dest_b" + str(battery - 1): 1.0}
        if action == "charge":
            if location == "start":
                if battery >= 2:
                    return {"start_b2": 1.0}
                return {"start_b" + str(battery + 1): 0.9, "start_b" + str(battery): 0.1}
            if battery <= 0:
                return {"failed": 1.0}
            return {state: 1.0}
        if location == "dest":
            if battery <= 0:
                return {"failed": 1.0}
            return {"delivered": 0.9, "dest_b" + str(battery - 1): 0.1}
        if battery <= 0:
            return {"failed": 1.0}
        return {location + "_b" + str(battery - 1): 1.0}

    def observation(self, state, joint_action, next_state, player):
        return str(next_state)

    def reward(self, state, joint_action, next_state, player):
        if next_state == "delivered":
            return 10.0
        if next_state == "failed":
            return -10.0
        return -1.0

    def is_terminal(self, state):
        return state in {"delivered", "failed"}

    def state_features(self, state):
        if state == "delivered":
            return {"battery": 0, "failed": False, "location": "dest", "package_delivered": True}
        if state == "failed":
            return {"battery": 0, "failed": True, "location": "unknown", "package_delivered": False}
        parts = state.split("_b")
        location = parts[0]
        battery = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return {"battery": battery, "failed": False, "location": location, "package_delivered": False}