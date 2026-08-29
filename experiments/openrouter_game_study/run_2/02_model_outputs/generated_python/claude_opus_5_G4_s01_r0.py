class GeneratedPOSG(AbstractPOSG):
    """Soccer penalty shootout: 3 rounds of simultaneous left/center/right choices.

    State encoding (strings only):
      "r{round}|{kicker_score}|{keeper_saves}"   -- decision states, round in 1..3
      "end|{kicker_score}|{keeper_saves}"        -- terminal state
    """

    ZONES = ["left", "center", "right"]
    ROUNDS = 3

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "r1|0|0"

    def _parse(self, state):
        parts = state.split("|")
        return parts[0], int(parts[1]), int(parts[2])

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return ["noop"]
        if player == "player_1":
            return ["shoot_left", "shoot_center", "shoot_right"]
        return ["dive_left", "stay_center", "dive_right"]

    def _zone(self, action):
        if action.endswith("left"):
            return "left"
        if action.endswith("right"):
            return "right"
        return "center"

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        tag, score, saves = self._parse(state)
        rnd = int(tag[1:])
        kz = self._zone(joint_action["player_1"])
        gz = self._zone(joint_action["player_2"])
        if kz == gz:
            # keeper in the same zone: save
            new_score, new_saves = score, saves + 1
        else:
            new_score, new_saves = score + 1, saves
        if rnd >= self.ROUNDS:
            return {"end|%d|%d" % (new_score, new_saves): 1.0}
        return {"r%d|%d|%d" % (rnd + 1, new_score, new_saves): 1.0}

    def observation(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return "game_over"
        tag, score, saves = self._parse(state)
        rnd = int(tag[1:])
        kz = self._zone(joint_action["player_1"])
        gz = self._zone(joint_action["player_2"])
        result = "save" if kz == gz else "goal"
        ntag, nscore, nsaves = self._parse(next_state)
        return (
            f"round={rnd};shot={kz};keeper={gz};result={result};"
            f"goals={nscore};saves={nsaves};next={'end' if ntag == 'end' else ntag}"
        )

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        kz = self._zone(joint_action["player_1"])
        gz = self._zone(joint_action["player_2"])
        goal = 1.0 if kz != gz else 0.0
        if player == "player_1":
            return goal
        return -goal

    def is_terminal(self, state):
        return state.startswith("end")
