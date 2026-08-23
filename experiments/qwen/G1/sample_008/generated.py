class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action):
        if joint_action["player_1"] == joint_action["player_2"]:
            return {"draw": 1.0}
        elif (joint_action["player_1"] == "rock" and joint_action["player_2"] == "scissors") or \
             (joint_action["player_1"] == "scissors" and joint_action["player_2"] == "paper") or \
             (joint_action["player_1"] == "paper" and joint_action["player_2"] == "rock"):
            return {"win": 1.0}
        else:
            return {"lose": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if next_state == "draw":
            return "It's a draw!"
        elif next_state == "win":
            return f"{player} wins!"
        else:
            return f"{player} loses!"
    def reward(self, state, joint_action, next_state, player):
        if next_state == "draw":
            return 0.0
        elif next_state == "win" and player == "player_1":
            return 1.0
        elif next_state == "win" and player == "player_2":
            return -1.0
        else:
            return -1.0
    def is_terminal(self, state): return state in ["draw", "win", "lose"]