class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["commander_1", "commander_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): 
        return [("0+3"), ("1+2"), ("2+1"), ("3+0")]
    def transition(self, state, joint_action):
        c1_alloc, c2_alloc = joint_action["commander_1"], joint_action["commander_2"]
        battlefield_wins_c1 = sum(1 for x in [c1_alloc, c2_alloc] if x > 3)
        battlefield_wins_c2 = sum(1 for x in [c1_alloc, c2_alloc] if x < 4)
        if battlefield_wins_c1 > battlefield_wins_c2:
            return {"commander_1_wins": 1.0}
        elif battlefield_wins_c1 < battlefield_wins_c2:
            return {"commander_2_wins": 1.0}
        else:
            return {"draw": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if next_state == "commander_1_wins":
            return f"{player} observes commander_1 wins"
        elif next_state == "commander_2_wins":
            return f"{player} observes commander_2 wins"
        else:
            return f"{player} observes draw"
    def reward(self, state, joint_action, next_state, player):
        if next_state == "commander_1_wins" and player == "commander_1":
            return 1.0
        elif next_state == "commander_2_wins" and player == "commander_2":
            return 1.0
        else:
            return 0.0
    def is_terminal(self, state):
        return state in ["commander_1_wins", "commander_2_wins", "draw"]