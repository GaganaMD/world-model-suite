class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "roll"

    def legal_actions(self, state, player):
        if state == "roll":
            return ["roll_die"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "roll":
            outcomes = {}
            p = 1.0 / 36.0
            for a in range(1, 7):
                for b in range(1, 7):
                    outcomes["result_%d_%d" % (a, b)] = p
                    
            # Ensure exact sum to 1.0
            keys = list(outcomes.keys())
            total = 0.0
            for k in keys[:-1]:
                total += outcomes[k]
            outcomes[keys[-1]] = 1.0 - total
            return outcomes
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "roll" and next_state.startswith("result_"):
            parts = next_state.split("_")
            a = parts[1]
            b = parts[2]
            if player == "player_1":
                return f"my_roll={a}|opp_roll={b}"
            return f"my_roll={b}|opp_roll={a}"
        return f"end|player={player}"

    def reward(self, state, joint_action, next_state, player):
        if state == "roll" and next_state.startswith("result_"):
            parts = next_state.split("_")
            a = int(parts[1])
            b = int(parts[2])
            if a > b:
                return 1.0 if player == "player_1" else -1.0
            if b > a:
                return -1.0 if player == "player_1" else 1.0
            return 0.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
