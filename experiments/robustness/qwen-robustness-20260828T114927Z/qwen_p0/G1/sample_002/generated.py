class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action): 
        if joint_action["player_1"] == joint_action["player_2"]:
            return {"terminal": 1.0}
        elif (joint_action["player_1"] == "rock" and joint_action["player_2"] == "scissors") or \
             (joint_action["player_1"] == "paper" and joint_action["player_2"] == "rock") or \
             (joint_action["player_1"] == "scissors" and joint_action["player_2"] == "paper"):
            return {"win": 0.5, "lose": 0.5}
        else:
            raise ValueError("Invalid joint action")
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "terminal":
            return f"{player} wins" if (joint_action[player] == "rock" and joint_action["other"] == "scissors") or \
                                      (joint_action[player] == "paper" and joint_action["other"] == "rock") or \
                                      (joint_action[player] == "scissors" and joint_action["other"] == "paper") else f"{player} loses"
        elif next_state == "win":
            return f"{player} wins"
        elif next_state == "lose":
            return f"{player} loses"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "terminal":
            return 1.0 if (joint_action[player] == "rock" and joint_action["other"] == "scissors") or \
                          (joint_action[player] == "paper" and joint_action["other"] == "rock") or \
                          (joint_action[player] == "scissors" and joint_action["other"] == "paper") else -1.0
        elif next_state == "win":
            return 1.0 if player == "player_1" else -1.0
        elif next_state == "lose":
            return -1.0 if player == "player_1" else 1.0
    def is_terminal(self, state): return state in ["terminal", "win", "lose"]