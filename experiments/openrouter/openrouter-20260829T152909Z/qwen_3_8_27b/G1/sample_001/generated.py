class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def is_terminal(self, state):
        return state == "terminal"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player == "player_1" or player == "player_2":
            return ["rock", "paper", "scissors"]
        return []

    def _winner(self, action_1, action_2):
        if action_1 not in ("rock", "paper", "scissors") or action_2 not in ("rock", "paper", "scissors"):
            return "tie"
        if action_1 == action_2:
            return "tie"
        if (
            (action_1 == "rock" and action_2 == "scissors")
            or (action_1 == "paper" and action_2 == "rock")
            or (action_1 == "scissors" and action_2 == "paper")
        ):
            return "player_1"
        return "player_2"

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        try:
            joint_action["player_1"]
            joint_action["player_2"]
        except (KeyError, TypeError):
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if player != "player_1" and player != "player_2":
            return "invalid"

        if not self.is_terminal(next_state):
            try:
                if player == "player_1":
                    own_action = joint_action["player_1"]
                else:
                    own_action = joint_action["player_2"]
            except (KeyError, TypeError):
                own_action = "unknown"
            return f"{player}:{own_action}:ongoing"

        try:
            action_1 = joint_action["player_1"]
            action_2 = joint_action["player_2"]
        except (KeyError, TypeError):
            return f"{player}:unknown:unknown"

        winner = self._winner(action_1, action_2)

        if player == "player_1":
            own_action = action_1
            if winner == "player_1":
                outcome = "win"
            elif winner == "player_2":
                outcome = "loss"
            else:
                outcome = "tie"
        else:
            own_action = action_2
            if winner == "player_2":
                outcome = "win"
            elif winner == "player_1":
                outcome = "loss"
            else:
                outcome = "tie"

        return f"{player}:{own_action}:{outcome}"

    def reward(self, state, joint_action, next_state, player):
        if player != "player_1" and player != "player_2":
            return 0.0

        if not self.is_terminal(next_state):
            return 0.0

        try:
            action_1 = joint_action["player_1"]
            action_2 = joint_action["player_2"]
        except (KeyError, TypeError):
            return 0.0

        winner = self._winner(action_1, action_2)

        if player == "player_1":
            if winner == "player_1":
                return 1.0
            if winner == "player_2":
                return -1.0
            return 0.0

        if winner == "player_2":
            return 1.0
        if winner == "player_1":
            return -1.0
        return 0.0