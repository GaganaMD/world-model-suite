class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "decision"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if state == "decision" and (
            player == "player_1" or player == "player_2"
        ):
            return ["hunt_stag", "hunt_hare"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]

        if action_1 == "hunt_stag" and action_2 == "hunt_stag":
            return {"terminal_both_stag": 1.0}
        if action_1 == "hunt_stag" and action_2 == "hunt_hare":
            return {"terminal_p1_stag_p2_hare": 1.0}
        if action_1 == "hunt_hare" and action_2 == "hunt_stag":
            return {"terminal_p1_hare_p2_stag": 1.0}
        return {"terminal_both_hare": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal_both_stag":
            return "stag_caught"
        if next_state == "terminal_both_hare":
            return "hare_caught"
        if next_state == "terminal_p1_stag_p2_hare":
            if player == "player_1":
                return "stag_failed"
            return "hare_caught"
        if next_state == "terminal_p1_hare_p2_stag":
            if player == "player_1":
                return "hare_caught"
            return "stag_failed"
        return "awaiting_choice"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "terminal_both_stag":
            return 4.0
        if next_state == "terminal_both_hare":
            return 1.0
        if next_state == "terminal_p1_stag_p2_hare":
            if player == "player_1":
                return 0.0
            return 1.0
        if next_state == "terminal_p1_hare_p2_stag":
            if player == "player_1":
                return 1.0
            return 0.0
        return 0.0

    def is_terminal(self, state):
        return (
            state == "terminal_both_stag"
            or state == "terminal_both_hare"
            or state == "terminal_p1_stag_p2_hare"
            or state == "terminal_p1_hare_p2_stag"
        )