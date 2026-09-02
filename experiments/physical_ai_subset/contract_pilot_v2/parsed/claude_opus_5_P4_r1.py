class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if player != "robot":
            return []
        if self.is_terminal(state):
            return []
        return ["safe_route", "risky_route"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        if isinstance(joint_action, dict):
            action = joint_action.get("robot")
        elif isinstance(joint_action, (list, tuple)):
            action = joint_action[0] if joint_action else None
        else:
            action = joint_action
        if action == "safe_route":
            return {"goal": 1.0}
        if action == "risky_route":
            return {"goal": 0.8, "collision": 0.2}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "goal":
            return "at_destination"
        if next_state == "collision":
            return "collided"
        return "en_route"

    def reward(self, state, joint_action, next_state, player):
        if player != "robot":
            return 0.0
        if self.is_terminal(state):
            return 0.0
        if isinstance(joint_action, dict):
            action = joint_action.get("robot")
        elif isinstance(joint_action, (list, tuple)):
            action = joint_action[0] if joint_action else None
        else:
            action = joint_action
        step_cost = -2.0 if action == "safe_route" else -1.0
        if next_state == "goal":
            return 10.0 + step_cost
        if next_state == "collision":
            return -20.0 + step_cost
        return step_cost

    def is_terminal(self, state):
        return state in {"goal", "collision"}