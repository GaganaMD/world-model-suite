class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): 
        return ["player_1", "player_2"]

    def initial_state(self): 
        return "start"

    def legal_actions(self, state, player): 
        return [str(i) for i in range(1, 7)]

    def transition(self, state, joint_action): 
        player1_roll = int(joint_action["player_1"])
        player2_roll = int(joint_action["player_2"])
        if player1_roll > player2_roll:
            return {"player_1_wins": 1.0}
        elif player2_roll > player1_roll:
            return {"player_2_wins": 1.0}
        else:
            return {"tie": 1.0}

    def observation(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins":
            return "player_1_wins"
        elif next_state == "player_2_wins":
            return "player_2_wins"
        else:
            return "tie"

    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins" and player == "player_1":
            return 1.0
        elif next_state == "player_2_wins" and player == "player_2":
            return 1.0
        else:
            return 0.0

    def is_terminal(self, state): 
        return state in ["player_1_wins", "player_2_wins", "tie"]