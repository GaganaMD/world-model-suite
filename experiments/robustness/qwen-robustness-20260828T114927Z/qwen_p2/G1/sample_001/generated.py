class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("rock", "rock")
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action):
        if joint_action["player_1"] == joint_action["player_2"]:
            return {"terminal": 1.0}
        elif (joint_action["player_1"], joint_action["player_2"]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            return {"win": 0.5, "lose": 0.5}
        else:
            raise ValueError("Invalid joint action")
    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            return "draw"
        elif (joint_action["player_1"], joint_action["player_2"]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            if player == "player_1" and joint_action["player_1"] > joint_action["player_2"]:
                return "win"
            elif player == "player_1":
                return "lose"
            else:
                return "win"
        else:
            raise ValueError("Invalid next state")
    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            return 0.0
        elif (joint_action["player_1"], joint_action["player_2"]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            if player == "player_1" and joint_action["player_1"] > joint_action["player_2"]:
                return 1.0
            elif player == "player_1":
                return -1.0
            else:
                return 1.0
        else:
            raise ValueError("Invalid next state")
    def is_terminal(self, state): return state[0] != state[1]