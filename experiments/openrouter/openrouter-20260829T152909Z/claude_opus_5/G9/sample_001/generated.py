class GeneratedPOSG(AbstractPOSG):
    """One-shot Colonel Blotto: 3 soldiers, 2 battlefields, simultaneous moves."""

    ALLOCATIONS = ("3-0", "2-1", "1-2", "0-3")

    @property
    def players(self):
        return ["player_1", "player_2"]

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _parse(action):
        left, right = action.split("-")
        return int(left), int(right)

    @classmethod
    def _outcome(cls, a1, a2):
        """Return 1 if player_1 wins the engagement, -1 if player_2, 0 draw."""
        p1_left, p1_right = cls._parse(a1)
        p2_left, p2_right = cls._parse(a2)

        wins1 = 0
        wins2 = 0
        if p1_left > p2_left:
            wins1 += 1
        elif p2_left > p1_left:
            wins2 += 1
        if p1_right > p2_right:
            wins1 += 1
        elif p2_right > p1_right:
            wins2 += 1

        if wins1 > wins2:
            return 1
        if wins2 > wins1:
            return -1
        return 0

    # ------------------------------------------------------------------ core API
    def initial_state(self):
        return "deploy"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        # Both commanders may choose any full allocation of three soldiers.
        return list(self.ALLOCATIONS)

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]

        if a1 not in self.ALLOCATIONS or a2 not in self.ALLOCATIONS:
            return {("end", "3-0", "3-0", 0): 1.0}

        result = self._outcome(a1, a2)
        return {("end", a1, a2, result): 1.0}

    def observation(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and len(next_state) == 4):
            return "no_report"

        _, a1, a2, result = next_state
        if player == "player_1":
            own, enemy = a1, a2
            score = result
        else:
            own, enemy = a2, a1
            score = -result

        if score > 0:
            verdict = "victory"
        elif score < 0:
            verdict = "defeat"
        else:
            verdict = "draw"

        return "own:" + own + "|enemy:" + enemy + "|" + verdict

    def reward(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and len(next_state) == 4):
            return 0.0
        result = next_state[3]
        if player == "player_1":
            return float(result)
        return float(-result)

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 4 and state[0] == "end"