class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action):
        if joint_action["player_1"] == joint_action["player_2"]:
            return {"terminal": 1.0}
        elif (joint_action["player_1"], joint_action["player_2"]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            return {"win": 1.0}
        else:
            return {"lose": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            return "draw"
        elif (joint_action["player_1"], joint_action["player_2"]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            if player == "player_1":
                return "win"
            else:
                return "lose"
        else:
            if player == "player_1":
                return "lose"
            else:
                return "win"
    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            return 0.0
        elif (joint_action["player_1"], joint_action["player_2"]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            if player == "player_1":
                return 1.0
            else:
                return -1.0
        else:
            if player == "player_1":
                return -1.0
            else:
                return 1.0
    def is_terminal(self, state): return state in ["terminal", "win", "lose"]