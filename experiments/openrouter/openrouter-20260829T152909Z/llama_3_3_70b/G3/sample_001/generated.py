class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "pre_flip"
    def legal_actions(self, state, player): 
        if state == "pre_flip":
            return ["heads", "tails"]
        else:
            return []
    def transition(self, state, joint_action): 
        if state == "pre_flip":
            outcomes = {"heads": 0.5, "tails": 0.5}
            return outcomes
        else:
            return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "heads":
            return f"{joint_action['player_1']}, {joint_action['player_2']}, heads"
        else:
            return f"{joint_action['player_1']}, {joint_action['player_2']}, tails"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == joint_action[player]:
            return 1.0
        elif joint_action["player_1"] == joint_action["player_2"]:
            return 0.0
        else:
            return -1.0
    def is_terminal(self, state): 
        return state != "pre_flip"