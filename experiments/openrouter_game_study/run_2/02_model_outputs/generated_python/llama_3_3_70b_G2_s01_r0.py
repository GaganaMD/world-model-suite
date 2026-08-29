class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["roll"]
        elif state.startswith("result_"): 
            return ["reset"]
        else: 
            return []
    def transition(self, state, joint_action): 
        if state == "start" and joint_action["player_1"] == "roll" and joint_action["player_2"] == "roll":
            outcomes = {}
            for roll1 in range(1, 7):
                for roll2 in range(1, 7):
                    outcome = f"result_{roll1}_{roll2}"
                    if outcome not in outcomes:
                        outcomes[outcome] = 0.0
                    outcomes[outcome] += 1.0 / 36.0
            return outcomes
        elif state.startswith("result_") and joint_action["player_1"] == "reset" and joint_action["player_2"] == "reset":
            return {"start": 1.0}
        else:
            return {}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start": 
            return "game_started"
        elif state.startswith("result_"): 
            roll1, roll2 = map(int, state.split("_")[1:])
            if roll1 > roll2:
                return f"player_1_wins_with_{roll1}"
            elif roll2 > roll1:
                return f"player_2_wins_with_{roll2}"
            else:
                return f"tie_with_{roll1}"
        else: 
            return ""
    def reward(self, state, joint_action, next_state, player): 
        if state == "start": 
            return 0.0
        elif state.startswith("result_"): 
            roll1, roll2 = map(int, state.split("_")[1:])
            if player == "player_1":
                if roll1 > roll2:
                    return 1.0
                elif roll2 > roll1:
                    return -1.0
                else:
                    return 0.0
            else:
                if roll1 > roll2:
                    return -1.0
                elif roll2 > roll1:
                    return 1.0
                else:
                    return 0.0
        else: 
            return 0.0
    def is_terminal(self, state): 
        return state.startswith("result_")
