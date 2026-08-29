class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["0_3", "1_2", "2_1", "3_0"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            p1_action = joint_action["player_1"]
            p2_action = joint_action["player_2"]
            p1_battlefield1 = int(p1_action.split("_")[0])
            p2_battlefield1 = int(p2_action.split("_")[0])
            if p1_battlefield1 > p2_battlefield1:
                return {"p1_wins": 1.0}
            elif p1_battlefield1 < p2_battlefield1:
                return {"p2_wins": 1.0}
            else:
                return {"draw": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            return f"deployed_{joint_action[player]}"
        return "game_over"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            if next_state == "p1_wins":
                return 1.0 if player == "player_1" else -1.0
            elif next_state == "p2_wins":
                return -1.0 if player == "player_1" else 1.0
            else:
                return 0.0
        return 0.0

    def is_terminal(self, state):
        return state in ["p1_wins", "p2_wins", "draw", "terminal"]
