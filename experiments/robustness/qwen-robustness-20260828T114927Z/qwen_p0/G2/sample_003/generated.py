class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return (0, 0)
    def legal_actions(self, state, player): return list(range(1, 7))
    def transition(self, state, joint_action):
        p1_roll, p2_roll = joint_action["player_1"], joint_action["player_2"]
        next_state = (p1_roll, p2_roll)
        if p1_roll > p2_roll:
            return {"(6, 6)": 0.0, "(5, 5)": 0.0, "(4, 4)": 0.0, "(3, 3)": 0.0, "(2, 2)": 0.0, "(1, 1)": 0.0, "terminal": 1.0}
        elif p1_roll < p2_roll:
            return {"(6, 6)": 0.0, "(5, 5)": 0.0, "(4, 4)": 0.0, "(3, 3)": 0.0, "(2, 2)": 0.0, "(1, 1)": 0.0, "terminal": 1.0}
        else:
            return {"(6, 6)": 0.0, "(5, 5)": 0.0, "(4, 4)": 0.0, "(3, 3)": 0.0, "(2, 2)": 0.0, "(1, 1)": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if player == "player_1":
            return f"Player 1 rolled {joint_action['player_1']}, Player 2 rolled {joint_action['player_2']}"
        else:
            return f"Player 1 rolled {joint_action['player_1']}, Player 2 rolled {joint_action['player_2']}"
    def reward(self, state, joint_action, next_state, player):
        p1_roll, p2_roll = joint_action["player_1"], joint_action["player_2"]
        if p1_roll > p2_roll and player == "player_1":
            return 1.0
        elif p1_roll < p2_roll and player == "player_2":
            return 1.0
        else:
            return 0.0
    def is_terminal(self, state): return state[0] != 0 or state[1] != 0