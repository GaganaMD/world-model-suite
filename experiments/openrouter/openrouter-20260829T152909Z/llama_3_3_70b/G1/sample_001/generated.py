class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action): 
        if state == "start":
            if joint_action["player_1"] == joint_action["player_2"]:
                return {"tie": 1.0}
            elif (joint_action["player_1"] == "rock" and joint_action["player_2"] == "scissors") or \
                 (joint_action["player_1"] == "scissors" and joint_action["player_2"] == "paper") or \
                 (joint_action["player_1"] == "paper" and joint_action["player_2"] == "rock"):
                return {"player_1_wins": 1.0}
            else:
                return {"player_2_wins": 1.0}
        else:
            return {}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "tie":
            return "It's a tie!"
        elif next_state == "player_1_wins":
            return "Player 1 wins!"
        else:
            return "Player 2 wins!"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins" and player == "player_1":
            return 1.0
        elif next_state == "player_2_wins" and player == "player_2":
            return 1.0
        else:
            return 0.0
    def is_terminal(self, state): return state in ["tie", "player_1_wins", "player_2_wins"]