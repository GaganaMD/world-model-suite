class GeneratedPOSG(AbstractPOSG):
    """
    Two players simultaneously roll one fair six-sided die each.
    The higher roll wins the round.

    States:
        "s0"                      -- pre-roll state (initial, non-terminal)
        ("done", d1, d2)          -- terminal state holding both die faces
    """

    DIE_FACES = (1, 2, 3, 4, 5, 6)

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        # The only decision available is to roll one's own die.
        return ["roll"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]

        # Both players roll; any legal action leads to the same uniform roll.
        if a1 == "roll" and a2 == "roll":
            prob = 1.0 / 36.0
            dist = {}
            for d1 in self.DIE_FACES:
                for d2 in self.DIE_FACES:
                    dist[("done", d1, d2)] = prob
            return dist

        # Defensive fallback: unrecognized actions still produce a valid roll.
        prob = 1.0 / 36.0
        dist = {}
        for d1 in self.DIE_FACES:
            for d2 in self.DIE_FACES:
                dist[("done", d1, d2)] = prob
        return dist

    def observation(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and len(next_state) == 3
                and next_state[0] == "done"):
            return "waiting_for_rolls"

        d1 = next_state[1]
        d2 = next_state[2]

        if player == "player_1":
            own, opp = d1, d2
        else:
            own, opp = d2, d1

        if own > opp:
            outcome = "win"
        elif own < opp:
            outcome = "lose"
        else:
            outcome = "tie"

        # Each player sees their own die face and the round outcome.
        return ("own_die", own, outcome)

    def reward(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and len(next_state) == 3
                and next_state[0] == "done"):
            return 0.0

        d1 = next_state[1]
        d2 = next_state[2]

        if player == "player_1":
            own, opp = d1, d2
        elif player == "player_2":
            own, opp = d2, d1
        else:
            return 0.0

        if own > opp:
            return 1.0
        if own < opp:
            return -1.0
        return 0.0

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 3 and state[0] == "done"