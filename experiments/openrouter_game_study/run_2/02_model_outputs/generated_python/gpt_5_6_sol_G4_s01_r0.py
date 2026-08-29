class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if player == "player_1":
            return ["shoot_left", "shoot_center", "shoot_right"]
        return ["dive_left", "stay_center", "dive_right"]

    def transition(self, state, joint_action):
        kicker = joint_action["player_1"]
        goalkeeper = joint_action["player_2"]
        matched = (
            (kicker == "shoot_left" and goalkeeper == "dive_left")
            or (kicker == "shoot_center" and goalkeeper == "stay_center")
            or (kicker == "shoot_right" and goalkeeper == "dive_right")
        )
        if matched:
            return {"terminal_saved": 1.0}
        return {"terminal_goal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal_saved":
            return "saved"
        if next_state == "terminal_goal":
            return "goal"
        return "penalty_ready"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal_goal":
            if player == "player_1":
                return 1.0
            return -1.0
        if next_state == "terminal_saved":
            if player == "player_1":
                return -1.0
            return 1.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal_goal" or state == "terminal_saved"
