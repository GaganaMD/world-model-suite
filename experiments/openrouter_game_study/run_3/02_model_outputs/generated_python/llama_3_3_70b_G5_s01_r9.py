class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): 
        if state == "s0":
            return ["heads", "tails"]
        elif state in ["hh", "ht", "th", "tt"]:
            return ["reveal"]
        else:
            return ["action"]
    def transition(self, state, joint_action): 
        if state == "s0":
            if joint_action["player_1"] == "heads" and joint_action["player_2"] == "heads":
                return {"hh": 1.0}
            elif joint_action["player_1"] == "heads" and joint_action["player_2"] == "tails":
                return {"ht": 1.0}
            elif joint_action["player_1"] == "tails" and joint_action["player_2"] == "heads":
                return {"th": 1.0}
            elif joint_action["player_1"] == "tails" and joint_action["player_2"] == "tails":
                return {"tt": 1.0}
            else:
                return {"s0": 1.0}
        elif state in ["hh", "ht", "th", "tt"]:
            if joint_action["player_1"] == "reveal" and joint_action["player_2"] == "reveal":
                return {"terminal": 1.0}
            else:
                return {"s0": 1.0}
        else:
            return {"s0": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if state == "s0":
            return "initial"
        elif state in ["hh", "ht", "th", "tt"]:
            if player == "player_1":
                return f"player_1_sees_{state}"
            elif player == "player_2":
                return f"player_2_sees_{state}"
        elif state == "terminal":
            if player == "player_1":
                if next_state == "hh" or next_state == "tt":
                    return "player_1_wins"
                else:
                    return "player_1_loses"
            elif player == "player_2":
                if next_state == "hh" or next_state == "tt":
                    return "player_2_loses"
                else:
                    return "player_2_wins"
        return "observation"
    def reward(self, state, joint_action, next_state, player): 
        if state == "terminal":
            if player == "player_1":
                if next_state == "hh" or next_state == "tt":
                    return 1.0
                else:
                    return -1.0
            elif player == "player_2":
                if next_state == "hh" or next_state == "tt":
                    return -1.0
                else:
                    return 1.0
        return 0.0
    def is_terminal(self, state): 
        return state == "terminal"
