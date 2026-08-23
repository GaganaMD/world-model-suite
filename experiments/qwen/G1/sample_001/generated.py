class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["Player1", "Player2"]

    def initial_state(self):
        return {}

    def legal_actions(self, state, player):
        return {"rock", "paper", "scissors"}

    def transition(self, state, joint_action):
        next_state = {}
        if joint_action["Player1"] == joint_action["Player2"]:
            next_state[state] = 1.0
        elif (joint_action["Player1"] == "rock" and joint_action["Player2"] == "scissors") or \
             (joint_action["Player1"] == "scissors" and joint_action["Player2"] == "paper") or \
             (joint_action["Player1"] == "paper" and joint_action["Player2"] == "rock"):
            next_state[joint_action["Player1"]] = 1.0
        else:
            next_state[joint_action["Player2"]] = 1.0
        return next_state

    def observation(self, state, joint_action, next_state, player):
        return joint_action[player]

    def reward(self, state, joint_action, next_state, player):
        if joint_action["Player1"] == joint_action["Player2"]:
            return 0.0
        elif (joint_action["Player1"] == "rock" and joint_action["Player2"] == "scissors") or \
             (joint_action["Player1"] == "scissors" and joint_action["Player2"] == "paper") or \
             (joint_action["Player1"] == "paper" and joint_action["Player2"] == "rock"):
            if player == "Player1":
                return 1.0
            else:
                return -1.0
        else:
            if player == "Player1":
                return -1.0
            else:
                return 1.0

    def is_terminal(self, state):
        return True