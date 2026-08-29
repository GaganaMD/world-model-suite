class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("rock", "paper")
    def legal_actions(self, state, player): return ["rock", "paper", "scissors"]
    def transition(self, state, joint_action):
        if joint_action == ("rock", "rock"):
            return {"(rock, rock)": 1.0}
        elif joint_action == ("rock", "paper"):
            return {"(rock, paper)": 1.0}
        elif joint_action == ("rock", "scissors"):
            return {"(rock, scissors)": 1.0}
        elif joint_action == ("paper", "rock"):
            return {"(paper, rock)": 1.0}
        elif joint_action == ("paper", "paper"):
            return {"(paper, paper)": 1.0}
        elif joint_action == ("paper", "scissors"):
            return {"(paper, scissors)": 1.0}
        elif joint_action == ("scissors", "rock"):
            return {"(scissors, rock)": 1.0}
        elif joint_action == ("scissors", "paper"):
            return {"(scissors, paper)": 1.0}
        elif joint_action == ("scissors", "scissors"):
            return {"(scissors, scissors)": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if player == "player_1":
            return f"Player 1 played {state[0]}, Player 2 played {next_state[1]}"
        else:
            return f"Player 2 played {state[1]}, Player 1 played {next_state[0]}"
    def reward(self, state, joint_action, next_state, player):
        if player == "player_1":
            if joint_action[0] == joint_action[1]:
                return 0.0
            elif (joint_action[0], joint_action[1]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
                return 1.0
            else:
                return -1.0
        else:
            if joint_action[0] == joint_action[1]:
                return 0.0
            elif (joint_action[0], joint_action[1]) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
                return -1.0
            else:
                return 1.0
    def is_terminal(self, state): return state == ("terminal", "terminal")