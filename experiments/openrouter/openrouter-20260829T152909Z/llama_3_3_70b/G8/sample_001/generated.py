class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "forest"
    def legal_actions(self, state, player): return ["hunt_stag", "hunt_hare"]
    def transition(self, state, joint_action): 
        if joint_action["player_1"] == "hunt_stag" and joint_action["player_2"] == "hunt_stag":
            return {"stag_caught": 1.0}
        elif joint_action["player_1"] == "hunt_hare" or joint_action["player_2"] == "hunt_hare":
            return {"hare_caught": 1.0}
        else:
            return {"nothing_caught": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "stag_caught":
            return "both_hunters_fed"
        elif next_state == "hare_caught":
            if joint_action[player] == "hunt_hare":
                return "hunter_fed"
            else:
                return "other_hunter_fed"
        else:
            return "no_hunter_fed"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "stag_caught":
            return 2.0
        elif next_state == "hare_caught":
            if joint_action[player] == "hunt_hare":
                return 1.0
            else:
                return 0.0
        else:
            return 0.0
    def is_terminal(self, state): 
        return state in ["stag_caught", "hare_caught", "nothing_caught"]