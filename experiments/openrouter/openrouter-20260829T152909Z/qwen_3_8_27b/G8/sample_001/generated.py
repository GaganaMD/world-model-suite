class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["stag", "hare"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]

        if action_1 == "stag" and action_2 == "stag":
            return {"stag_caught": 1.0}

        if action_1 == "hare" and action_2 == "hare":
            return {"both_hare": 1.0}

        if action_1 == "hare" and action_2 == "stag":
            return {"hare_player_1": 1.0}

        if action_1 == "stag" and action_2 == "hare":
            return {"hare_player_2": 1.0}

        return {"s0": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "stag_caught":
            return "stag_caught"

        if next_state == "both_hare":
            return "hare_caught"

        if next_state == "hare_player_1":
            if player == "player_1":
                return "hare_caught"
            return "stag_failed"

        if next_state == "hare_player_2":
            if player == "player_2":
                return "hare_caught"
            return "stag_failed"

        return "unknown"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "stag_caught":
            return 10.0

        if next_state == "both_hare":
            return 1.0

        if next_state == "hare_player_1":
            if player == "player_1":
                return 1.0
            return 0.0

        if next_state == "hare_player_2":
            if player == "player_2":
                return 1.0
            return 0.0

        return 0.0

    def is_terminal(self, state):
        return state in ("stag_caught", "both_hare", "hare_player_1", "hare_player_2")