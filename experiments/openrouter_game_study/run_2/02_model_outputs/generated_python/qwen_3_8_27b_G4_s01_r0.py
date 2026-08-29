class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["kicker", "goalkeeper"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            if player == "kicker":
                return ["shoot_left", "shoot_center", "shoot_right"]
            elif player == "goalkeeper":
                return ["dive_left", "stay_center", "dive_right"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            return {"terminal": 1.0}
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            kicker_action = joint_action.get("kicker", "unknown")
            keeper_action = joint_action.get("goalkeeper", "unknown")
            if player == "kicker":
                return f"shot:{kicker_action};dive:{keeper_action}"
            elif player == "goalkeeper":
                return f"shot:{kicker_action};dive:{keeper_action}"
        return "terminal"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            kicker_action = joint_action.get("kicker", "")
            keeper_action = joint_action.get("goalkeeper", "")
            # Map actions to zones
            kicker_zone = {
                "shoot_left": "left",
                "shoot_center": "center",
                "shoot_right": "right"
            }.get(kicker_action, "unknown")
            keeper_zone = {
                "dive_left": "left",
                "stay_center": "center",
                "dive_right": "right"
            }.get(keeper_action, "unknown")
            
            if kicker_zone == keeper_zone:
                # Goalkeeper saved it
                if player == "kicker":
                    return -1.0
                else:
                    return 1.0
            else:
                # Goal scored
                if player == "kicker":
                    return 1.0
                else:
                    return -1.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
