class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["heads", "tails"]

    def transition(self, state, joint_action):
        if state == "s0":
            first = joint_action["player_1"]
            second = joint_action["player_2"]
            if first == second:
                return {"terminal_player_1_wins": 1.0}
            return {"terminal_player_2_wins": 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal_player_1_wins":
            return "same_faces_player_1_wins"
        if next_state == "terminal_player_2_wins":
            return "different_faces_player_2_wins"
        return "game_start"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal_player_1_wins":
            return 1.0 if player == "player_1" else -1.0
        if next_state == "terminal_player_2_wins":
            return 1.0 if player == "player_2" else -1.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal_player_1_wins" or state == "terminal_player_2_wins"
