class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "s_start_free"

    def legal_actions(self, state, player):
        return ["move", "pick_up", "drop", "deliver"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        f = self.state_features(state)
        robot = f["robot_location"]
        obj = f["object_location"]
        carrying = f["carrying"]

        if action == "move":
            new_robot = "dest" if robot == "start" else "start"
            if carrying:
                return {self._encode(new_robot, new_robot, True, False, False): 0.9,
                        self._encode(new_robot, new_robot, False, True, False): 0.1}
            return {self._encode(new_robot, obj, False, False, False): 1.0}

        if action == "pick_up":
            if carrying or robot != obj:
                return {state: 1.0}
            return {self._encode(robot, robot, True, False, False): 0.85,
                    self._encode(robot, robot, False, False, False): 0.1,
                    self._encode(robot, robot, False, True, False): 0.05}

        if action == "drop":
            if not carrying:
                return {state: 1.0}
            return {self._encode(robot, robot, False, False, False): 0.7,
                    self._encode(robot, robot, False, True, False): 0.3}

        if action == "deliver":
            if not carrying or robot != "dest":
                return {state: 1.0}
            return {self._encode("dest", "dest", False, False, True): 0.9,
                    self._encode("dest", "dest", False, True, False): 0.1}

        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        f = self.state_features(next_state)
        return "|".join([
            "robot=" + f["robot_location"],
            "obj=" + f["object_location"],
            "carry=" + str(f["carrying"]),
            "broken=" + str(f["broken"]),
            "delivered=" + str(f["delivered"]),
        ])

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        prev = self.state_features(state)
        nxt = self.state_features(next_state)
        r = -1.0
        if nxt["broken"] and not prev["broken"]:
            r += -20.0
        if nxt["delivered"] and not prev["delivered"]:
            r += 30.0
        return r

    def is_terminal(self, state):
        f = self.state_features(state)
        return bool(f["broken"]) or bool(f["delivered"])

    def state_features(self, state):
        parts = str(state).split("_")
        if len(parts) != 3 or parts[0] != "s":
            return {"broken": False, "carrying": False, "delivered": False,
                    "object_location": "start", "robot_location": "start"}
        robot = parts[1] if parts[1] in ("start", "dest") else "start"
        tag = parts[2]
        if tag == "broken":
            return {"broken": True, "carrying": False, "delivered": False,
                    "object_location": robot, "robot_location": robot}
        if tag == "delivered":
            return {"broken": False, "carrying": False, "delivered": True,
                    "object_location": "dest", "robot_location": "dest"}
        if tag == "carry":
            return {"broken": False, "carrying": True, "delivered": False,
                    "object_location": robot, "robot_location": robot}
        return {"broken": False, "carrying": False, "delivered": False,
                "object_location": robot, "robot_location": robot}

    def _encode(self, robot, obj, carrying, broken, delivered):
        if broken:
            return "s_" + str(robot) + "_broken"
        if delivered:
            return "s_dest_delivered"
        if carrying:
            return "s_" + str(robot) + "_carry"
        return "s_" + str(robot) + "_free"