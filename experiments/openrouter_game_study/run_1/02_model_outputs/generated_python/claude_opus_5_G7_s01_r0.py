class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["suspect_a", "suspect_b"]

    def initial_state(self):
        return "interrogation"

    def legal_actions(self, state, player):
        if state == "interrogation":
            return ["silent", "testify"]
        return ["wait"]

    def transition(self, state, joint_action):
        if state == "interrogation":
            a = joint_action["suspect_a"]
            b = joint_action["suspect_b"]
            a = a if a in ("silent", "testify") else "silent"
            b = b if b in ("silent", "testify") else "silent"
            return {f"verdict_{a}_{b}": 1.0}
        return {"verdict_silent_silent": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "interrogation":
            own = joint_action.get(player, "silent")
            return f"decided:{own}|awaiting_verdict"
        return f"verdict:{next_state}"

    def reward(self, state, joint_action, next_state, player):
        if state != "interrogation":
            return 0.0
        a = joint_action["suspect_a"]
        b = joint_action["suspect_b"]
        a = a if a in ("silent", "testify") else "silent"
        b = b if b in ("silent", "testify") else "silent"
        own = a if player == "suspect_a" else b
        other = b if player == "suspect_a" else a
        if own == "silent" and other == "silent":
            return -1.0
        if own == "testify" and other == "testify":
            return -5.0
        if own == "testify" and other == "silent":
            return 0.0
        return -10.0

    def is_terminal(self, state):
        return state.startswith("verdict_")
