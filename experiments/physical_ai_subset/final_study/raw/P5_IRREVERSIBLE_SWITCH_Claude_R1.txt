class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "start_closed"

    def legal_actions(self, state, player):
        return ["move", "press_switch"]

    def transition(self, state, joint_action):
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        if self.is_terminal(state):
            return {state: 1.0}
        if state == "start_closed":
            if action == "press_switch":
                return {"start_open": 0.9, "start_closed": 0.1}
            return {"corridor_closed": 0.8, "start_closed": 0.2}
        if state == "start_open":
            if action == "press_switch":
                return {"start_open": 1.0}
            return {"corridor_open": 0.9, "start_open": 0.1}
        if state == "corridor_closed":
            if action == "press_switch":
                return {"corridor_open": 0.7, "corridor_closed": 0.3}
            return {"blocked_closed": 0.6, "corridor_closed": 0.4}
        if state == "corridor_open":
            if action == "press_switch":
                return {"corridor_open": 1.0}
            return {"target_reached": 0.85, "corridor_open": 0.15}
        if state == "blocked_closed":
            if action == "press_switch":
                return {"blocked_open": 0.8, "blocked_closed": 0.2}
            return {"blocked_closed": 1.0}
        if state == "blocked_open":
            if action == "press_switch":
                return {"blocked_open": 1.0}
            return {"target_reached": 0.9, "blocked_open": 0.1}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        features = self.state_features(next_state)
        return "loc=" + features["location"] + "|open=" + str(features["access_open"]) + "|switch=" + str(features["switch_pressed"])

    def reward(self, state, joint_action, next_state, player):
        if next_state == "target_reached" and state != "target_reached":
            return 10.0
        if next_state == state:
            return -0.5
        return -0.1

    def is_terminal(self, state):
        return state in {"target_reached"}

    def state_features(self, state):
        table = {
            "start_closed": {"access_open": False, "goal_reached": False, "location": "start", "switch_pressed": False},
            "start_open": {"access_open": True, "goal_reached": False, "location": "start", "switch_pressed": True},
            "corridor_closed": {"access_open": False, "goal_reached": False, "location": "corridor", "switch_pressed": False},
            "corridor_open": {"access_open": True, "goal_reached": False, "location": "corridor", "switch_pressed": True},
            "blocked_closed": {"access_open": False, "goal_reached": False, "location": "gate", "switch_pressed": False},
            "blocked_open": {"access_open": True, "goal_reached": False, "location": "gate", "switch_pressed": True},
            "target_reached": {"access_open": True, "goal_reached": True, "location": "target", "switch_pressed": True},
        }
        return dict(table.get(state, {"access_open": False, "goal_reached": False, "location": "start", "switch_pressed": False}))