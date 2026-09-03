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
                return {self._encode("midway", battery - 1): 0.8,
                        self._encode("start", battery - 1): 0.2}
            if location == "midway":
                return {self._encode("destination", battery - 1): 0.8,
                        self._encode("midway", battery - 1): 0.2}
            return {self._encode("midway", battery - 1): 0.8,
                    self._encode("destination", battery - 1): 0.2}
        if action == "charge":
            if location == "start":
                if battery >= 2:
                    return {self._encode("start", 2): 1.0}
                return {self._encode("start", battery + 1): 0.9,
                        self._encode("start", battery): 0.1}
            if battery <= 0:
                return {"failed": 1.0}
            return {self._encode(location, battery - 1): 1.0}
        if action == "deliver":
            if location == "destination":
                if battery <= 0:
                    return {"failed": 1.0}
                return {"delivered": 0.9,
                        self._encode("destination", battery - 1): 0.1}
            if battery <= 0:
                return {"failed": 1.0}
            return {self._encode(location, battery - 1): 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        feats = self.state_features(next_state)
        return "loc=" + feats["location"] + ";bat=" + str(feats["battery"]) + \
               ";done=" + str(feats["package_delivered"]) + ";fail=" + str(feats["failed"])

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        if next_state == "delivered":
            return 10.0
        if next_state == "failed":
            return -10.0
        if action == "charge":
            return -0.5
        return -1.0

    def is_terminal(self, state):
        return state in {"delivered", "failed"}

    def state_features(self, state):
        if state == "delivered":
            return {"battery": 0, "failed": False, "location": "destination", "package_delivered": True}
        if state == "failed":
            return {"battery": 0, "failed": True, "location": "unknown", "package_delivered": False}
        parts = state.split("_b")
        location = parts[0] if len(parts) == 2 else "start"
        try:
            battery = int(parts[1])
        except (IndexError, ValueError):
            battery = 0
        if battery < 0:
            battery = 0
        if battery > 2:
            battery = 2
        return {"battery": battery, "failed": False, "location": location, "package_delivered": False}

    def _encode(self, location, battery):
        if battery < 0:
            battery = 0
        if battery > 2:
            battery = 2
        return location + "_b" + str(battery)