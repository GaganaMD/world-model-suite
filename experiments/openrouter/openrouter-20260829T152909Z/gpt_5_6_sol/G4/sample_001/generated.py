class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "ready"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player == "player_1":
            return ["shoot_left", "shoot_center", "shoot_right"]
        if player == "player_2":
            return ["dive_left", "stay_center", "dive_right"]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        shot_zone = {
            "shoot_left": "left",
            "shoot_center": "center",
            "shoot_right": "right",
        }[joint_action["player_1"]]
        keeper_zone = {
            "dive_left": "left",
            "stay_center": "center",
            "dive_right": "right",
        }[joint_action["player_2"]]

        if shot_zone == keeper_zone:
            return {("terminal", "saved", shot_zone, keeper_zone): 1.0}
        return {("terminal", "goal", shot_zone, keeper_zone): 1.0}

    def observation(self, state, joint_action, next_state, player):
        if player not in self.players:
            return "invalid_player"
        if self.is_terminal(next_state):
            return (next_state[1], next_state[2], next_state[3])
        return "awaiting_kick"

    def reward(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return 0.0
        goal = next_state[1] == "goal"
        if player == "player_1":
            return 1.0 if goal else -1.0
        if player == "player_2":
            return -1.0 if goal else 1.0
        return 0.0

    def is_terminal(self, state):
        return (
            isinstance(state, tuple)
            and len(state) == 4
            and state[0] == "terminal"
        )