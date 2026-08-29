class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        # Both players have the same two actions in the only non-terminal state.
        return ["silent", "testify"]

    def transition(self, state, joint_action):
        # One-shot game: any joint action leads to the terminal state with probability 1.
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # No observation information is needed; return a constant string.
        return "no_obs"

    def reward(self, state, joint_action, next_state, player):
        # Payoffs based on the standard Prisoner's Dilemma matrix.
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]

        if a1 == "silent" and a2 == "silent":
            # Both stay silent: light sentence (reward 3 each)
            return 3
        elif a1 == "testify" and a2 == "testify":
            # Both testify: heavy sentence (reward 1 each)
            return 1
        elif a1 == "testify" and a2 == "silent":
            # Player 1 testifies, player 2 silent: player 1 goes free (5), player 2 max (0)
            return 5 if player == "player_1" else 0
        elif a1 == "silent" and a2 == "testify":
            # Player 1 silent, player 2 testifies: player 1 max (0), player 2 goes free (5)
            return 0 if player == "player_1" else 5
        else:
            # Should never happen, but return 0 for safety.
            return 0

    def is_terminal(self, state):
        return state == "terminal"
