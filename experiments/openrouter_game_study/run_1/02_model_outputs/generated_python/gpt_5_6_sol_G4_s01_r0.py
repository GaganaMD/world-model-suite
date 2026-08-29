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
        shot = joint_action["player_1"]
        save = joint_action["player_2"]
        shot_zone = shot.replace("shoot_", "")
        save_zone = save.replace("dive_", "").replace("stay_", "")
        if shot_zone == save_zone:
            return {"terminal_saved": 1.0}
        return {"terminal_goal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return f"{joint_action['player_1']}|{joint_action['player_2']}|{next_state}"

    def reward(self, state, joint_action, next_state, player):
        goal = next_state == "terminal_goal"
        if player == "player_1":
            return 1.0 if goal else -1.0
        return -1.0 if goal else 1.0

    def is_terminal(self, state):
        return state == "terminal_goal" or state == "terminal_saved"
