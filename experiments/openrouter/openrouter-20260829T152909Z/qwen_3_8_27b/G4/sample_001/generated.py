class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if player == "player_1":
            return ["left", "center", "right"]
        if player == "player_2":
            return ["left", "center", "right"]
        return []

    def transition(self, state, joint_action):
        if state == "s0":
            kick = joint_action["player_1"]
            dive = joint_action["player_2"]
            next_state = "save" if kick == dive else "goal"
            return {next_state: 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if player == "player_1":
            return ("player_1", joint_action["player_1"], next_state)
        if player == "player_2":
            return ("player_2", joint_action["player_2"], next_state)
        return next_state

    def reward(self, state, joint_action, next_state, player):
        if next_state == "goal":
            return 1.0 if player == "player_1" else 0.0
        if next_state == "save":
            return 0.0 if player == "player_1" else 1.0
        return 0.0

    def is_terminal(self, state):
        return state in ("goal", "save")