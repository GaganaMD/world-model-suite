class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "start"

    def legal_actions(self, state, player):
        if state == "start":
            return ["stag", "hare"]
        return []  # terminal state has no legal actions

    def transition(self, state, joint_action):
        if state == "start":
            # Always transition to terminal with probability 1
            return {"terminal": 1.0}
        return {}  # terminal state has no transitions

    def observation(self, state, joint_action, next_state, player):
        # Both players observe the same initial state; no further observations
        return "start" if state == "start" else "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state != "start":
            return 0.0
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        if a1 == "stag" and a2 == "stag":
            return 4.0
        elif a1 == "stag" and a2 == "hare":
            return 0.0 if player == "player_1" else 1.0
        elif a1 == "hare" and a2 == "stag":
            return 1.0 if player == "player_1" else 0.0
        else:  # both hare
            return 1.0

    def is_terminal(self, state):
        return state == "terminal"