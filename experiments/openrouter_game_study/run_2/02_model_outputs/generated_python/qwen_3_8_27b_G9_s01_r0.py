class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        # Actions represent allocation of 3 soldiers to battlefield A (and 3 - a to B)
        # a can be 0, 1, 2, 3
        return ["a0", "a1", "a2", "a3"]

    def transition(self, state, joint_action):
        # Deterministic transition to terminal state
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # In a simultaneous move game, players observe their own action and the outcome
        # We encode the joint action and the result in the observation string
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        
        # Calculate soldiers on battlefield A for each
        s1_a = int(a1[1])
        s2_a = int(a2[1])
        
        # Determine winner of battlefield A
        if s1_a > s2_a:
            bf_a_winner = "player_1"
        elif s2_a > s1_a:
            bf_a_winner = "player_2"
        else:
            bf_a_winner = "draw"
            
        # Calculate soldiers on battlefield B for each
        s1_b = 3 - s1_a
        s2_b = 3 - s2_a
        
        # Determine winner of battlefield B
        if s1_b > s2_b:
            bf_b_winner = "player_1"
        elif s2_b > s1_b:
            bf_b_winner = "player_2"
        else:
            bf_b_winner = "draw"
            
        # Determine overall winner
        p1_wins = 0
        p2_wins = 0
        if bf_a_winner == "player_1":
            p1_wins += 1
        elif bf_a_winner == "player_2":
            p2_wins += 1
            
        if bf_b_winner == "player_1":
            p1_wins += 1
        elif bf_b_winner == "player_2":
            p2_wins += 1
            
        if p1_wins > p2_wins:
            overall = "player_1_wins"
        elif p2_wins > p1_wins:
            overall = "player_2_wins"
        else:
            overall = "draw"
            
        return f"obs_{player}_a1={a1}_a2={a2}_bf_a={bf_a_winner}_bf_b={bf_b_winner}_overall={overall}"

    def reward(self, state, joint_action, next_state, player):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        
        s1_a = int(a1[1])
        s2_a = int(a2[1])
        
        if s1_a > s2_a:
            bf_a_winner = "player_1"
        elif s2_a > s1_a:
            bf_a_winner = "player_2"
        else:
            bf_a_winner = "draw"
            
        s1_b = 3 - s1_a
        s2_b = 3 - s2_a
        
        if s1_b > s2_b:
            bf_b_winner = "player_1"
        elif s2_b > s1_b:
            bf_b_winner = "player_2"
        else:
            bf_b_winner = "draw"
            
        p1_wins = 0
        p2_wins = 0
        if bf_a_winner == "player_1":
            p1_wins += 1
        elif bf_a_winner == "player_2":
            p2_wins += 1
            
        if bf_b_winner == "player_1":
            p1_wins += 1
        elif bf_b_winner == "player_2":
            p2_wins += 1
            
        if player == "player_1":
            if p1_wins > p2_wins:
                return 1.0
            elif p1_wins < p2_wins:
                return -1.0
            else:
                return 0.0
        else:
            if p2_wins > p1_wins:
                return 1.0
            elif p2_wins < p1_wins:
                return -1.0
            else:
                return 0.0

    def is_terminal(self, state):
        return state == "terminal"
