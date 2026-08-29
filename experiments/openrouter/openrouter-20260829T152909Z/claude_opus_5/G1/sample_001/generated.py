class GeneratedPOSG(AbstractPOSG):
    """Single round of rock-paper-scissors.

    States:
        "start"                      -- both players have yet to throw (non-terminal)
        ("end", a1, a2)              -- terminal state recording the revealed throws
    """

    ACTIONS = ("rock", "paper", "scissors")

    # Maps (own_action, other_action) -> +1 win, 0 draw, -1 loss
    BEATS = {
        ("rock", "scissors"): 1,
        ("scissors", "paper"): 1,
        ("paper", "rock"): 1,
    }

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "start"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        return list(self.ACTIONS)

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = joint_action.get("player_1", "rock")
        a2 = joint_action.get("player_2", "rock")
        if a1 not in self.ACTIONS:
            a1 = "rock"
        if a2 not in self.ACTIONS:
            a2 = "rock"
        return {("end", a1, a2): 1.0}

    def observation(self, state, joint_action, next_state, player):
        if not isinstance(next_state, tuple) or next_state[0] != "end":
            return ("waiting",)

        a1 = next_state[1]
        a2 = next_state[2]
        if player == "player_1":
            own, other = a1, a2
        else:
            own, other = a2, a1

        if own == other:
            result = "draw"
        elif self.BEATS.get((own, other), 0) == 1:
            result = "win"
        else:
            result = "loss"
        return ("reveal", own, other, result)

    def reward(self, state, joint_action, next_state, player):
        if not isinstance(next_state, tuple) or next_state[0] != "end":
            return 0.0

        a1 = next_state[1]
        a2 = next_state[2]
        if player == "player_1":
            own, other = a1, a2
        else:
            own, other = a2, a1

        if own == other:
            return 0.0
        if self.BEATS.get((own, other), 0) == 1:
            return 1.0
        return -1.0

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 3 and state[0] == "end"