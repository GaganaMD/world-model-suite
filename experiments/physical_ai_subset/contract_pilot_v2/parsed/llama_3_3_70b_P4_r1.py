class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["robot"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["safe_route", "risky_route"]
    def transition(self, state, joint_action): 
        if joint_action == "safe_route":
            return {"goal": 1.0}
        elif joint_action == "risky_route":
            return {"goal": 0.8, "collision": 0.2}
    def observation(self, state, joint_action, next_state, player): return str(next_state)
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "goal":
            return 1.0
        elif next_state == "collision":
            return -1.0
        else:
            return 0.0
    def is_terminal(self, state): return state in {"goal", "collision"}