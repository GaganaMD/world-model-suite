class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player in ("player_1", "player_2"):
            return ["heads", "tails"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        p1 = joint_action["player_1"]
        p2 = joint_action["player_2"]

        if p1 == p2:
            return {"terminal_same": 1.0}
        return {"terminal_different": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if not isinstance(joint_action, dict):
            return "s0"

        try:
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
        except KeyError:
            return "s0"

        if player == "player_1":
            return (p1, p2)
        if player == "player_2":
            return (p2, p1)
        return (p1, p2)

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal_same":
            same = True
        elif next_state == "terminal_different":
            same = False
        else:
            if not isinstance(joint_action, dict):
                return 0.0
            try:
                same = joint_action["player_1"] == joint_action["player_2"]
            except KeyError:
                return 0.0

        if player == "player_1":
            return 1.0 if same else -1.0
        if player == "player_2":
            return -1.0 if same else 1.0
        return 0.0

    def is_terminal(self, state):
        return state in ("terminal_same", "terminal_different")