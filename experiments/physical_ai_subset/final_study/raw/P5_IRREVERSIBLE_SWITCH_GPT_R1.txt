class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "start_closed"
    def legal_actions(self, state, player):
        if state == "start_closed":
            return ["move", "press_switch"]
        if state == "switch_closed":
            return ["move", "press_switch"]
        if state == "start_open":
            return ["move", "press_switch"]
        return []
    def transition(self, state, joint_action):
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action
        if state == "start_closed":
            return {"switch_closed": 1.0} if action == "move" else {"start_open": 1.0}
        if state == "switch_closed":
            return {"start_closed": 1.0} if action == "move" else {"start_open": 1.0}
        if state == "start_open":
            return {"goal": 1.0} if action == "move" else {"start_open": 1.0}
        return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player): return 1.0 if next_state == "goal" else 0.0
    def is_terminal(self, state): return state == "goal"
    def state_features(self, state):
        if state == "start_closed":
            return {"access_open": False, "goal_reached": False, "location": "start", "switch_pressed": False}
        if state == "switch_closed":
            return {"access_open": False, "goal_reached": False, "location": "switch", "switch_pressed": False}
        if state == "start_open":
            return {"access_open": True, "goal_reached": False, "location": "start", "switch_pressed": True}
        return {"access_open": True, "goal_reached": True, "location": "target", "switch_pressed": True}