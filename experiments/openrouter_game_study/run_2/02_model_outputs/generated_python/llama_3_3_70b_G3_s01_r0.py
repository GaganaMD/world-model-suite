class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["heads", "tails"]
        elif state in ["player_1_wins", "player_2_wins", "draw"]: 
            return []
    def transition(self, state, joint_action): 
        if state == "start": 
            outcome = "heads" if joint_action["player_1"] == joint_action["player_2"] else "tails" if joint_action["player_1"]!= joint_action["player_2"] else "draw"
            if outcome == "heads": 
                return {"player_1_wins": 0.5, "player_2_wins": 0.5}
            elif outcome == "tails": 
                return {"player_1_wins": 0.5, "player_2_wins": 0.5}
            else: 
                return {"draw": 1.0}
        else: 
            return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start": 
            return f"{player} called {joint_action[player]} and the coin landed {next_state}"
        else: 
            return f"{player} is in state {next_state}"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "player_1_wins": 
            return 1.0 if player == "player_1" else -1.0
        elif next_state == "player_2_wins": 
            return -1.0 if player == "player_1" else 1.0
        else: 
            return 0.0
    def is_terminal(self, state): 
        return state!= "start"
