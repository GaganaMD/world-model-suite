class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["hunt_stag", "hunt_hare"]

    def transition(self, state, joint_action):
        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]
        if action_1 == "hunt_stag" and action_2 == "hunt_stag":
            return {"terminal_stag": 1.0}
        if action_1 == "hunt_hare" and action_2 == "hunt_hare":
            return {"terminal_both_hare": 1.0}
        if action_1 == "hunt_stag":
            return {"terminal_p1_stag_p2_hare": 1.0}
        return {"terminal_p1_hare_p2_stag": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return f"{next_state}"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal_stag":
            return 4.0
        if next_state == "terminal_both_hare":
            return 2.0
        if next_state == "terminal_p1_stag_p2_hare":
            return 0.0 if player == "player_1" else 2.0
        if next_state == "terminal_p1_hare_p2_stag":
            return 2.0 if player == "player_1" else 0.0
        return 0.0

    def is_terminal(self, state):
        return state.startswith("terminal_")
