class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        # Each commander allocates 3 soldiers between two battlefields.
        # Action is a string representing (soldiers_to_bf1, soldiers_to_bf2)
        # where bf1 + bf2 = 3.
        return ["0_3", "1_2", "2_1", "3_0"]

    def transition(self, state, joint_action):
        # Deterministic transition to terminal state
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # In a simultaneous move game, each player observes their own action
        # and the outcome (which battlefields they won)
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        
        # Parse actions
        s1_bf1, s1_bf2 = map(int, a1.split("_"))
        s2_bf1, s2_bf2 = map(int, a2.split("_"))
        
        # Determine battlefield winners
        bf1_winner = "player_1" if s1_bf1 > s2_bf1 else ("player_2" if s2_bf1 > s1_bf1 else "draw")
        bf2_winner = "player_1" if s1_bf2 > s2_bf2 else ("player_2" if s2_bf2 > s1_bf2 else "draw")
        
        # Determine overall winner
        p1_wins = (bf1_winner == "player_1") + (bf2_winner == "player_1")
        p2_wins = (bf1_winner == "player_2") + (bf2_winner == "player_2")
        
        if p1_wins > p2_wins:
            overall = "player_1_wins"
        elif p2_wins > p1_wins:
            overall = "player_2_wins"
        else:
            overall = "draw"
        
        # Observation includes own action and overall outcome
        own_action = a1 if player == "player_1" else a2
        return f"action={own_action},outcome={overall}"

    def reward(self, state, joint_action, next_state, player):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        
        s1_bf1, s1_bf2 = map(int, a1.split("_"))
        s2_bf1, s2_bf2 = map(int, a2.split("_"))
        
        bf1_winner = "player_1" if s1_bf1 > s2_bf1 else ("player_2" if s2_bf1 > s1_bf1 else "draw")
        bf2_winner = "player_1" if s1_bf2 > s2_bf2 else ("player_2" if s2_bf2 > s1_bf2 else "draw")
        
        p1_wins = (bf1_winner == "player_1") + (bf2_winner == "player_1")
        p2_wins = (bf1_winner == "player_2") + (bf2_winner == "player_2")
        
        if p1_wins > p2_wins:
            winner = "player_1"
        elif p2_wins > p1_wins:
            winner = "player_2"
        else:
            winner = "draw"
        
        if player == "player_1":
            if winner == "player_1":
                return 1.0
            elif winner == "player_2":
                return -1.0
            else:
                return 0.0
        else:
            if winner == "player_2":
                return 1.0
            elif winner == "player_1":
                return -1.0
            else:
                return 0.0

    def is_terminal(self, state):
        return state == "terminal"
