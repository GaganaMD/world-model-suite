class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action):
        action1 = joint_action["player_1"]
        action2 = joint_action["player_2"]
        if action1 == action2:
            return {"s0": 0.5, "terminal_draw": 0.5}
        elif (action1 == "rock" and action2 == "scissors") or \
             (action1 == "paper" and action2 == "rock") or \
             (action1 == "scissors" and action2 == "paper"):
            return {"s0": 0.8, "terminal_win": 0.2}
        else:
            return {"s0": 0.2, "terminal_lose": 0.8}
    def observation(self, state, joint_action, next_state, player):
        action1 = joint_action["player_1"]
        action2 = joint_action["player_2"]
        if player == "player_1":
            return f"Player 1 sees {action1} and Player 2 sees {action2}"
        else:
            return f"Player 2 sees {action2} and Player 1 sees {action1}"
    def reward(self, state, joint_action, next_state, player):
        action1 = joint_action["player_1"]
        action2 = joint_action["player_2"]
        if action1 == action2:
            return 0.0
        elif (action1 == "rock" and action2 == "scissors") or \
             (action1 == "paper" and action2 == "rock") or \
             (action1 == "scissors" and action2 == "paper"):
            if player == "player_1":
                return 1.0
            else:
                return -1.0
        else:
            if player == "player_1":
                return -1.0
            else:
                return 1.0
    def is_terminal(self, state): return state in ["terminal_draw", "terminal_win", "terminal_lose"]