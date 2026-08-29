class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action):
        action1 = joint_action["player_1"]
        action2 = joint_action["player_2"]
        if (action1 == "rock" and action2 == "scissors") or \
           (action1 == "scissors" and action2 == "paper") or \
           (action1 == "paper" and action2 == "rock"):
            return {"win": 1.0}
        elif action1 == action2:
            return {"draw": 1.0}
        else:
            return {"lose": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if next_state == "win":
            if player == "player_1":
                return "You win!"
            else:
                return "Player 2 wins!"
        elif next_state == "draw":
            return "It's a draw!"
        else:
            if player == "player_1":
                return "You lose!"
            else:
                return "Player 2 loses!"
    def reward(self, state, joint_action, next_state, player):
        if next_state == "win":
            return 1.0
        elif next_state == "draw":
            return 0.0
        else:
            return -1.0
    def is_terminal(self, state): return state in ["win", "draw", "lose"]