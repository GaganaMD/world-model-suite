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
            # Both calls are either heads or tails; fair coin flip
            return {"s1": 0.5, "s2": 0.5}
        if state == "s1":
            # Coin result: heads
            return {"terminal": 1.0}
        if state == "s2":
            # Coin result: tails
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            # Before the flip, players observe nothing about the coin
            return "no_observation"
        if state == "s1":
            # Coin result heads; player sees their own call and the result
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            if player == "player_1":
                return f"heads_result_my_call_{p1}"
            else:
                return f"heads_result_my_call_{p2}"
        if state == "s2":
            # Coin result tails
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            if player == "player_1":
                return f"tails_result_my_call_{p1}"
            else:
                return f"tails_result_my_call_{p2}"
        return "terminal_observation"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            return 0.0
        if state == "s1":
            # Coin result heads
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            p1_wins = (p1 == "heads")
            p2_wins = (p2 == "heads")
            if p1_wins and p2_wins:
                return 0.0  # draw
            if p1_wins:
                return 1.0 if player == "player_1" else -1.0
            if p2_wins:
                return -1.0 if player == "player_1" else 1.0
            return 0.0  # neither matches
        if state == "s2":
            # Coin result tails
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            p1_wins = (p1 == "tails")
            p2_wins = (p2 == "tails")
            if p1_wins and p2_wins:
                return 0.0  # draw
            if p1_wins:
                return 1.0 if player == "player_1" else -1.0
            if p2_wins:
                return -1.0 if player == "player_1" else 1.0
            return 0.0  # neither matches
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
