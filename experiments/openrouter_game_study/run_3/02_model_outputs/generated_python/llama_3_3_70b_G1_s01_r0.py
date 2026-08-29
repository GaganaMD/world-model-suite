class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["rock", "paper", "scissors"]
        elif state == "player_1_wins" or state == "player_2_wins" or state == "tie":
            return []
    def transition(self, state, joint_action): 
        if state == "start":
            player_1_action = joint_action["player_1"]
            player_2_action = joint_action["player_2"]
            if player_1_action == player_2_action:
                return {"tie": 1.0}
            elif (player_1_action == "rock" and player_2_action == "scissors") or \
                 (player_1_action == "scissors" and player_2_action == "paper") or \
                 (player_1_action == "paper" and player_2_action == "rock"):
                return {"player_1_wins": 1.0}
            else:
                return {"player_2_wins": 1.0}
        else:
            return {}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start":
            return f"{player} played {joint_action[player]}"
        else:
            return f"Game over, {next_state}"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins":
            return 1.0 if player == "player_1" else -1.0
        elif next_state == "player_2_wins":
            return 1.0 if player == "player_2" else -1.0
        elif next_state == "tie":
            return 0.0
        else:
            return 0.0
    def is_terminal(self, state): 
        return state!= "start"
