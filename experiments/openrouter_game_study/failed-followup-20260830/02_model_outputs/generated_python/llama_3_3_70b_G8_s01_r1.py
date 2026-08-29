class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["hunter_1", "hunter_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["hunt_stag", "hunt_hare"]
        elif state == "both_hunt_stag": 
            return ["eat_stag"]
        elif state == "one_hunts_stag": 
            return ["go_home"]
        elif state == "one_hunts_hare": 
            return ["eat_hare"]
        elif state == "terminal": 
            return []
        else: 
            return ["hunt_stag", "hunt_hare"]
    def transition(self, state, joint_action): 
        if state == "start": 
            if joint_action["hunter_1"] == "hunt_stag" and joint_action["hunter_2"] == "hunt_stag": 
                return {"both_hunt_stag": 1.0}
            elif joint_action["hunter_1"] == "hunt_stag" and joint_action["hunter_2"] == "hunt_hare": 
                return {"one_hunts_stag": 1.0}
            elif joint_action["hunter_1"] == "hunt_hare" and joint_action["hunter_2"] == "hunt_stag": 
                return {"one_hunts_stag": 1.0}
            else: 
                return {"one_hunts_hare": 1.0}
        elif state == "both_hunt_stag": 
            return {"terminal": 1.0}
        elif state == "one_hunts_stag": 
            return {"terminal": 1.0}
        elif state == "one_hunts_hare": 
            return {"terminal": 1.0}
        elif state == "terminal": 
            return {"terminal": 1.0}
        else: 
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "both_hunt_stag": 
            return f"both_hunters_caught_stag"
        elif next_state == "one_hunts_stag": 
            return f"one_hunter_wasted_effort"
        elif next_state == "one_hunts_hare": 
            return f"one_hunter_caught_hare"
        elif next_state == "terminal": 
            return f"game_over"
        else: 
            return f"unknown_state"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "both_hunt_stag": 
            return 2.0
        elif next_state == "one_hunts_stag": 
            return 0.0
        elif next_state == "one_hunts_hare": 
            if player == "hunter_1" and joint_action["hunter_1"] == "hunt_hare": 
                return 1.0
            elif player == "hunter_2" and joint_action["hunter_2"] == "hunt_hare": 
                return 1.0
            else: 
                return 0.0
        elif next_state == "terminal": 
            return 0.0
        else: 
            return 0.0
    def is_terminal(self, state): 
        return state == "terminal"
