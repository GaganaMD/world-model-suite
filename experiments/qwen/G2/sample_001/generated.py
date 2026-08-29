class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return (0, 0)
    def legal_actions(self, state, player): return list(range(1, 7))
    def transition(self, state, joint_action):
        p1_roll, p2_roll = joint_action["player_1"], joint_action["player_2"]
        if p1_roll > p2_roll:
            next_state = "p1_wins"
        elif p2_roll > p1_roll:
            next_state = "p2_wins"
        else:
            next_state = "tie"
        return {next_state: 1.0}
    def observation(self, state, joint_action, next_state, player):
        if next_state == "p1_wins":
            return f"Player 1 wins with a roll of {joint_action['player_1']}"
        elif next_state == "p2_wins":
            return f"Player 2 wins with a roll of {joint_action['player_2']}"
        else:
            return f"It's a tie with rolls of {joint_action['player_1']} and {joint_action['player_2']}"
    def reward(self, state, joint_action, next_state, player):
        if next_state == "p1_wins":
            return 1.0 if player == "player_1" else -1.0
        elif next_state == "p2_wins":
            return 1.0 if player == "player_2" else -1.0
        else:
            return 0.0
    def is_terminal(self, state): return state in ["p1_wins", "p2_wins", "tie"]