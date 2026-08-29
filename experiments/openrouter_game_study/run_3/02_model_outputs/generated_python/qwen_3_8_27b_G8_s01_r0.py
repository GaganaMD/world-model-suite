class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "terminal":
            return []
        # Both players can choose to hunt stag or hare
        return ["hunt_stag", "hunt_hare"]

    def transition(self, state, joint_action):
        if state == "terminal":
            return {"terminal": 1.0}
        
        p1_action = joint_action.get("player_1")
        p2_action = joint_action.get("player_2")
        
        # Determine outcome based on actions
        if p1_action == "hunt_stag" and p2_action == "hunt_stag":
            next_state = "terminal_both_stag"
        elif p1_action == "hunt_stag" and p2_action == "hunt_hare":
            next_state = "terminal_p1_stag_p2_hare"
        elif p1_action == "hunt_hare" and p2_action == "hunt_stag":
            next_state = "terminal_p1_hare_p2_stag"
        else:  # both hunt hare
            next_state = "terminal_both_hare"
        
        return {next_state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "terminal":
            return f"game_over_{player}"
        
        p1_action = joint_action.get("player_1")
        p2_action = joint_action.get("player_2")
        
        if player == "player_1":
            if p1_action == "hunt_stag" and p2_action == "hunt_stag":
                return "I hunted stag and caught it with partner"
            elif p1_action == "hunt_stag" and p2_action == "hunt_hare":
                return "I hunted stag but partner hunted hare, I got nothing"
            elif p1_action == "hunt_hare" and p2_action == "hunt_stag":
                return "I hunted hare and caught it alone"
            else:
                return "I hunted hare and caught it alone"
        else:  # player_2
            if p1_action == "hunt_stag" and p2_action == "hunt_stag":
                return "I hunted stag and caught it with partner"
            elif p1_action == "hunt_stag" and p2_action == "hunt_hare":
                return "I hunted hare and caught it alone"
            elif p1_action == "hunt_hare" and p2_action == "hunt_stag":
                return "I hunted stag but partner hunted hare, I got nothing"
            else:
                return "I hunted hare and caught it alone"

    def reward(self, state, joint_action, next_state, player):
        if state == "terminal":
            return 0.0
        
        p1_action = joint_action.get("player_1")
        p2_action = joint_action.get("player_2")
        
        if player == "player_1":
            if p1_action == "hunt_stag" and p2_action == "hunt_stag":
                return 10.0  # Stag feeds well
            elif p1_action == "hunt_stag" and p2_action == "hunt_hare":
                return 0.0   # Lone hunter cannot bring down stag
            elif p1_action == "hunt_hare" and p2_action == "hunt_stag":
                return 5.0   # Hare feeds one person
            else:
                return 5.0   # Both hunt hare
        else:  # player_2
            if p1_action == "hunt_stag" and p2_action == "hunt_stag":
                return 10.0  # Stag feeds well
            elif p1_action == "hunt_stag" and p2_action == "hunt_hare":
                return 5.0   # Hare feeds one person
            elif p1_action == "hunt_hare" and p2_action == "hunt_stag":
                return 0.0   # Lone hunter cannot bring down stag
            else:
                return 5.0   # Both hunt hare

    def is_terminal(self, state):
        return state.startswith("terminal")
