class GeneratedPOSG(AbstractPOSG):
    """Matching Pennies as a one-shot simultaneous-move POSG.

    States:
        "s0"                      -- both pennies still hidden (initial, non-terminal)
        ("end", f1, f2)           -- terminal state recording the revealed faces
    """

    FACES = ("heads", "tails")

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        # Both players secretly place their penny heads-up or tails-up.
        return ["heads", "tails"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]

        if a1 not in self.FACES:
            a1 = "heads"
        if a2 not in self.FACES:
            a2 = "heads"

        return {("end", a1, a2): 1.0}

    def observation(self, state, joint_action, next_state, player):
        # Placement is secret; the reveal happens on transition into the terminal state.
        if isinstance(next_state, tuple) and next_state[0] == "end":
            f1 = next_state[1]
            f2 = next_state[2]
            outcome = "match" if f1 == f2 else "mismatch"
            if player == "player_1":
                return ("reveal", "my_face:" + f1, "their_face:" + f2, outcome)
            return ("reveal", "my_face:" + f2, "their_face:" + f1, outcome)
        return ("hidden", "pennies_not_yet_revealed")

    def reward(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and next_state[0] == "end"):
            return 0.0
        if self.is_terminal(state):
            return 0.0

        matched = next_state[1] == next_state[2]
        # Player 1 wins both pennies on a match, player 2 wins them on a mismatch.
        if player == "player_1":
            return 1.0 if matched else -1.0
        if player == "player_2":
            return -1.0 if matched else 1.0
        return 0.0

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 3 and state[0] == "end"