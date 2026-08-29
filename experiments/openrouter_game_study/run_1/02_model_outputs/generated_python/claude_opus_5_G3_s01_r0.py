class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "call"

    def legal_actions(self, state, player):
        if state == "call":
            return ["heads", "tails"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "call":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 not in ("heads", "tails"):
                a1 = "heads"
            if a2 not in ("heads", "tails"):
                a2 = "heads"
            return {
                f"end_{a1}_{a2}_heads": 0.5,
                f"end_{a1}_{a2}_tails": 0.5,
            }
        return {"end_heads_heads_heads": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "call" and next_state.startswith("end_"):
            parts = next_state.split("_")
            a1, a2, coin = parts[1], parts[2], parts[3]
            own = a1 if player == "player_1" else a2
            other = a2 if player == "player_1" else a1
            return f"coin={coin}|my_call={own}|other_call={other}"
        return f"terminal|player={player}"

    def reward(self, state, joint_action, next_state, player):
        if state != "call" or not next_state.startswith("end_"):
            return 0.0
        parts = next_state.split("_")
        a1, a2, coin = parts[1], parts[2], parts[3]
        m1 = 1 if a1 == coin else 0
        m2 = 1 if a2 == coin else 0
        if m1 == m2:
            return 0.0
        if player == "player_1":
            return 1.0 if m1 == 1 else -1.0
        return 1.0 if m2 == 1 else -1.0

    def is_terminal(self, state):
        return state.startswith("end_")
