class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "deploy"

    def legal_actions(self, state, player):
        if state == "deploy":
            return ["3-0", "2-1", "1-2", "0-3"]
        return ["noop"]

    def _split(self, action):
        parts = action.split("-")
        return int(parts[0]), int(parts[1])

    def _outcome(self, a1, a2):
        x1, y1 = self._split(a1)
        x2, y2 = self._split(a2)
        score = 0
        if x1 > x2:
            score += 1
        elif x2 > x1:
            score -= 1
        if y1 > y2:
            score += 1
        elif y2 > y1:
            score -= 1
        if score > 0:
            return "win1"
        if score < 0:
            return "win2"
        return "draw"

    def transition(self, state, joint_action):
        if state == "deploy":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 not in ("3-0", "2-1", "1-2", "0-3"):
                a1 = "3-0"
            if a2 not in ("3-0", "2-1", "1-2", "0-3"):
                a2 = "3-0"
            res = self._outcome(a1, a2)
            return {"end_" + res + "_" + a1 + "_" + a2: 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state != "deploy":
            return "terminal"
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        own = a1 if player == "player_1" else a2
        opp = a2 if player == "player_1" else a1
        res = "draw"
        if next_state.startswith("end_win1_"):
            res = "win1"
        elif next_state.startswith("end_win2_"):
            res = "win2"
        if res == "draw":
            label = "draw"
        elif (res == "win1" and player == "player_1") or (res == "win2" and player == "player_2"):
            label = "victory"
        else:
            label = "defeat"
        return f"own={own};opp={opp};result={label}"

    def reward(self, state, joint_action, next_state, player):
        if state != "deploy":
            return 0.0
        if next_state.startswith("end_win1_"):
            return 1.0 if player == "player_1" else -1.0
        if next_state.startswith("end_win2_"):
            return -1.0 if player == "player_1" else 1.0
        return 0.0

    def is_terminal(self, state):
        return state.startswith("end_")
