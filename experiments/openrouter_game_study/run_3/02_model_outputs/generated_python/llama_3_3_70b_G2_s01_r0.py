class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["roll"]
        elif state.startswith("player_1_rolls_") or state.startswith("player_2_rolls_"):
            return []
    def transition(self, state, joint_action): 
        if state == "start":
            outcomes = {}
            for roll_1 in range(1, 7):
                for roll_2 in range(1, 7):
                    outcome_state = f"player_1_rolls_{roll_1}_player_2_rolls_{roll_2}"
                    if outcome_state not in outcomes:
                        outcomes[outcome_state] = 0.0
                    outcomes[outcome_state] += 1/36
            return outcomes
        else:
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start":
            return "dice_not_rolled"
        else:
            rolls = next_state.split("_")
            player_1_roll = int(rolls[3])
            player_2_roll = int(rolls[6])
            if player == "player_1":
                return f"you_rolled_{player_1_roll}_opponent_rolled_{player_2_roll}"
            else:
                return f"you_rolled_{player_2_roll}_opponent_rolled_{player_1_roll}"
    def reward(self, state, joint_action, next_state, player): 
        if state == "start":
            return 0.0
        else:
            rolls = next_state.split("_")
            player_1_roll = int(rolls[3])
            player_2_roll = int(rolls[6])
            if player == "player_1":
                if player_1_roll > player_2_roll:
                    return 1.0
                elif player_1_roll < player_2_roll:
                    return -1.0
                else:
                    return 0.0
            else:
                if player_2_roll > player_1_roll:
                    return 1.0
                elif player_2_roll < player_1_roll:
                    return -1.0
                else:
                    return 0.0
    def is_terminal(self, state): 
        return not state == "start"
