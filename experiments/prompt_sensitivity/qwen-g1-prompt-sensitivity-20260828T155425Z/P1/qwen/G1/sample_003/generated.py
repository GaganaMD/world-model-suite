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
            return {"s0": 0.7, "terminal_win": 0.3}
        else:
            return {"s0": 0.3, "terminal_lose": 0.7}
    def observation(self, state, joint_action, next_state, player):
        action = joint_action[player]
        if next_state == "terminal_draw":
            return f"{player} observed a draw"
        elif next_state == "terminal_win":
            return f"{player} observed a win"
        elif next_state == "terminal_lose":
            return f"{player} observed a loss"
        else:
            return f"{player} observed {action}"
    def reward(self, state, joint_action, next_state, player):
        action = joint_action[player]
        if next_state == "terminal_draw":
            return 0.0
        elif next_state == "terminal_win":
            return 1.0
        elif next_state == "terminal_lose":
            return -1.0
    def is_terminal(self, state): return state in ["terminal_draw", "terminal_win", "terminal_lose"]