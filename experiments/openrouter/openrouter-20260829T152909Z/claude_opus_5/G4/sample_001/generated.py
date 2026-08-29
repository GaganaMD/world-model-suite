class GeneratedPOSG(AbstractPOSG):
    """
    One-shot simultaneous-move penalty kick.

    player_1 = kicker  : shoots "left", "center", or "right"
    player_2 = keeper  : dives "left", "right", or stays "center"

    The kick scores unless the keeper commits to the same zone as the shot,
    in which case the shot is saved.

    States:
        "s0"     -> pre-kick world configuration (non-terminal)
        "goal"   -> terminal, kicker scored
        "save"   -> terminal, keeper saved the shot
    """

    KICKER = "player_1"
    KEEPER = "player_2"

    ZONES = ("left", "center", "right")

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player == self.KICKER:
            return ["shoot_left", "shoot_center", "shoot_right"]
        if player == self.KEEPER:
            return ["dive_left", "stay_center", "dive_right"]
        return []

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #
    def _kick_zone(self, action):
        if action == "shoot_left":
            return "left"
        if action == "shoot_right":
            return "right"
        return "center"

    def _keeper_zone(self, action):
        if action == "dive_left":
            return "left"
        if action == "dive_right":
            return "right"
        return "center"

    # ------------------------------------------------------------------ #
    # dynamics
    # ------------------------------------------------------------------ #
    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        kick = self._kick_zone(joint_action[self.KICKER])
        keep = self._keeper_zone(joint_action[self.KEEPER])

        if kick == keep:
            return {"save": 1.0}
        return {"goal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return "match_over"

        kick = self._kick_zone(joint_action[self.KICKER])
        keep = self._keeper_zone(joint_action[self.KEEPER])
        outcome = "goal" if next_state == "goal" else "save"

        # Both participants see where the ball went, where the keeper went,
        # and the result of the kick.
        if player == self.KICKER:
            return ("kicker_view", kick, keep, outcome)
        if player == self.KEEPER:
            return ("keeper_view", kick, keep, outcome)
        return ("spectator_view", outcome)

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0

        scored = (next_state == "goal")

        if player == self.KICKER:
            return 1.0 if scored else -1.0
        if player == self.KEEPER:
            return -1.0 if scored else 1.0
        return 0.0

    def is_terminal(self, state):
        return state in ("goal", "save")