class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "start_closed"

    def legal_actions(self, state, player):
        if player != "robot":
            return []
        if self.is_terminal(state):
            return []
        return ["move", "press_switch"]

    def transition(self, state, joint_action):
        action = joint_action.get("robot") if isinstance(joint_action, dict) else joint_action
        if self.is_terminal(state):
            return {state: 1.0}
        if state == "start_closed":
            if action == "press_switch":
                return {"start_open": 0.9, "start_closed": 0.1}
            if action == "move":
                return {"corridor_closed": 0.8, "start_closed": 0.2}
            return {state: 1.0}
        if state == "start_open":
            if action == "press_switch":
                return {"start_open": 1.0}
            if action == "move":
                return {"corridor_open": 0.9, "start_open": 0.1}
            return {state: 1.0}
        if state == "corridor_closed":
            if action == "press_switch":
                return {"corridor_open": 0.85, "corridor_closed": 0.15}
            if action == "move":
                return {"blocked_dead_end": 0.7, "corridor_closed": 0.3}
            return {state: 1.0}
        if state == "corridor_open":
            if action == "press_switch":
                return {"corridor_open": 1.0}
            if action == "move":
                return {"goal": 0.9, "corridor_open": 0.1}
            return {state: 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        features = self.state_features(next_state)
        return "|".join([
            str(features["location"]),
            "switch_pressed" if features["switch_pressed"] else "switch_unpressed",
            "access_open" if features["access_open"] else "access_closed",
            "goal" if features["goal_reached"] else "no_goal",
        ])

    def reward(self, state, joint_action, next_state, player):
        if player != "robot":
            return 0.0
        if next_state == "goal" and state != "goal":
            return 10.0
        if next_state == "blocked_dead_end" and state != "blocked_dead_end":
            return -5.0
        if self.is_terminal(state):
            return 0.0
        return -1.0

    def is_terminal(self, state):
        return state in {"goal", "blocked_dead_end"}

    def state_features(self, state):
        table = {
            "start_closed": {"access_open": False, "goal_reached": False, "location": "start", "switch_pressed": False},
            "start_open": {"access_open": True, "goal_reached": False, "location": "start", "switch_pressed": True},
            "corridor_closed": {"access_open": False, "goal_reached": False, "location": "corridor", "switch_pressed": False},
            "corridor_open": {"access_open": True, "goal_reached": False, "location": "corridor", "switch_pressed": True},
            "goal": {"access_open": True, "goal_reached": True, "location": "target", "switch_pressed": True},
            "blocked_dead_end": {"access_open": False, "goal_reached": False, "location": "dead_end", "switch_pressed": False},
        }
        return dict(table.get(state, {"access_open": False, "goal_reached": False, "location": "start", "switch_pressed": False}))