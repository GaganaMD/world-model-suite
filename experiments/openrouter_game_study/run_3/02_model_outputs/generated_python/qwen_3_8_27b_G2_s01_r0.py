class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["roll"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            # Both players roll a fair six-sided die simultaneously.
            # The joint outcome is determined by chance (uniform over 36 combinations).
            # We encode the next state as a string representing the dice values.
            # Since the game is a single round, the next state is terminal.
            # We need to return a distribution over next states.
            # Each next state is "d1_d2" where d1 is player_1's die and d2 is player_2's die.
            # There are 36 possible outcomes, each with probability 1/36.
            dist = {}
            for d1 in range(1, 7):
                for d2 in range(1, 7):
                    next_state = f"{d1}_{d2}"
                    dist[next_state] = 1.0 / 36.0
            return dist
        else:
            # Should not be reached for non-terminal states other than s0
            return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # The player observes their own die roll.
        # next_state is of the form "d1_d2"
        if "_" in next_state:
            parts = next_state.split("_")
            d1 = parts[0]
            d2 = parts[1]
            if player == "player_1":
                return f"my_roll={d1}"
            else:
                return f"my_roll={d2}"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        # Reward is determined by who rolled higher.
        # Winner gets +1, loser gets -1, tie gets 0.
        if "_" in next_state:
            parts = next_state.split("_")
            d1 = int(parts[0])
            d2 = int(parts[1])
            if player == "player_1":
                if d1 > d2:
                    return 1.0
                elif d1 < d2:
                    return -1.0
                else:
                    return 0.0
            else:
                if d2 > d1:
                    return 1.0
                elif d2 < d1:
                    return -1.0
                else:
                    return 0.0
        return 0.0

    def is_terminal(self, state):
        # All states after the initial roll are terminal.
        # The initial state "s0" is non-terminal.
        # All other states (of the form "d1_d2") are terminal.
        return state != "s0"
