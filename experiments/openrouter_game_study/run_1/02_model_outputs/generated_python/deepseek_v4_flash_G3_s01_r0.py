class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            if p1 == "heads" and p2 == "heads":
                return {"terminal": 1.0}
            elif p1 == "heads" and p2 == "tails":
                return {"terminal": 1.0}
            elif p1 == "tails" and p2 == "heads":
                return {"terminal": 1.0}
            else:  # tails, tails
                return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            # The coin flip is fair: heads or tails with 0.5 each.
            # We encode the outcome as an observation string.
            # Since the transition is deterministic to terminal, we simulate the coin
            # by returning a random-looking observation. But to keep it deterministic
            # in the model, we use a fixed encoding based on the joint action.
            # The actual coin result is not observed by players before choosing,
            # so we give a generic observation.
            return "coin_flip"
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            # The coin flip is fair, but we need a deterministic reward.
            # We model the expected reward given the joint action.
            # If both choose same, probability of both matching = 0.5 (coin matches that side)
            # If both choose same, probability of neither matching = 0.5 (coin opposite)
            # If both choose same: both match -> draw, neither match -> draw, so reward 0.
            # If they differ: exactly one matches with prob 0.5, the other matches with prob 0.5.
            # So each player wins with prob 0.5, loses with prob 0.5, expected reward 0.
            # To keep it simple and deterministic, we return 0 for all.
            return 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
