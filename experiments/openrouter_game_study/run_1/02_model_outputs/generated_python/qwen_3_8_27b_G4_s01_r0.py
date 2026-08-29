class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["kicker", "goalkeeper"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "terminal":
            return ["noop"]
        if player == "kicker":
            return ["shoot_left", "shoot_center", "shoot_right"]
        elif player == "goalkeeper":
            return ["dive_left", "stay_center", "dive_right"]
        else:
            return ["noop"]

    def transition(self, state, joint_action):
        if state == "terminal":
            return {"terminal": 1.0}
        
        kick = joint_action.get("kicker", "shoot_center")
        goal = joint_action.get("goalkeeper", "stay_center")
        
        # Determine outcome based on zones
        # Zones: left, center, right
        kick_zone = None
        if kick == "shoot_left":
            kick_zone = "left"
        elif kick == "shoot_center":
            kick_zone = "center"
        elif kick == "shoot_right":
            kick_zone = "right"
            
        goal_zone = None
        if goal == "dive_left":
            goal_zone = "left"
        elif goal == "stay_center":
            goal_zone = "center"
        elif goal == "dive_right":
            goal_zone = "right"
            
        if kick_zone == goal_zone:
            next_state = "saved"
        else:
            next_state = "goal"
            
        return {next_state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            return "game_over"
            
        kick = joint_action.get("kicker", "shoot_center")
        goal = joint_action.get("goalkeeper", "stay_center")
        
        if player == "kicker":
            # Kicker sees their own action and the result (goal or saved)
            if next_state == "goal":
                return f"kick:{kick},result:goal"
            else:
                return f"kick:{kick},result:saved"
        elif player == "goalkeeper":
            # Goalkeeper sees their own action and the result
            if next_state == "goal":
                return f"dive:{goal},result:goal"
            else:
                return f"dive:{goal},result:saved"
        else:
            return "unknown"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            return 0.0
            
        if next_state == "goal":
            # Kicker scores, goalkeeper concedes
            if player == "kicker":
                return 1.0
            elif player == "goalkeeper":
                return -1.0
        else:
            # Saved
            if player == "kicker":
                return -1.0
            elif player == "goalkeeper":
                return 1.0
                
        return 0.0

    def is_terminal(self, state):
        return state in ("goal", "saved")
