class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "initial"

    def legal_actions(self, state, player):
        if state == "initial":
            return ["0,3", "1,2", "2,1", "3,0"]
        else:
            return []  # terminal state has no legal actions

    def transition(self, state, joint_action):
        if state == "initial":
            # The game is deterministic: always ends in terminal state.
            return {"terminal": 1.0}
        else:
            # Should not be called on terminal states, but return a valid dict.
            return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # In this one-shot game, the observation is simply the current state.
        return state

    def reward(self, state, joint_action, next_state, player):
        if state != "initial":
            return 0.0  # No reward after the game ends

        # Parse allocations
        a1, b1 = map(int, joint_action["player_1"].split(","))
        a2, b2 = map(int, joint_action["player_2"].split(","))

        # Determine battlefield wins
        wins1 = 0
        wins2 = 0
        if a1 > a2:
            wins1 += 1
        elif a1 < a2:
            wins2 += 1
        if b1 > b2:
            wins1 += 1
        elif b1 < b2:
            wins2 += 1

        # Overall outcome
        if wins1 > wins2:
            outcome = 1  # player_1 wins
        elif wins1 < wins2:
            outcome = -1  # player_2 wins
        else:
            outcome = 0  # draw

        if player == "player_1":
            return float(outcome)
        elif player == "player_2":
            return float(-outcome)
        else:
            raise ValueError(f"Unknown player: {player}")

    def is_terminal(self, state):
        return state == "terminal"