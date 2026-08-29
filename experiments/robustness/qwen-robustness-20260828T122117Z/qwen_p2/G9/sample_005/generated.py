class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["commander_1", "commander_2"]
    def initial_state(self): return ("s0", 0, 0)
    def legal_actions(self, state, player):
        if player == "commander_1":
            return [(i, 3 - i) for i in range(4)]
        else:
            return [(j, 3 - j) for j in range(4)]
    def transition(self, state, joint_action):
        next_state = self._next_state(state, joint_action)
        if self.is_terminal(next_state):
            return {"terminal": 1.0}
        else:
            return {next_state: 1.0}
    def observation(self, state, joint_action, next_state, player):
        result = self._determine_outcome(joint_action)
        if player == "commander_1":
            return f"Commander 1 {'wins' if result[0] > result[1] else 'loses'}"
        else:
            return f"Commander 2 {'wins' if result[1] > result[0] else 'loses'}"
    def reward(self, state, joint_action, next_state, player):
        result = self._determine_outcome(joint_action)
        if player == "commander_1":
            return (1.0, -1.0) if result[0] > result[1] else (-1.0, 1.0)
        else:
            return (-1.0, 1.0) if result[1] > result[0] else (1.0, -1.0)
    def is_terminal(self, state):
        _, c1_wins, c2_wins = state
        return c1_wins == 2 or c2_wins == 2

    def _next_state(self, state, joint_action):
        _, c1_alloc, c2_alloc = state
        c1_wins = max(c1_alloc[0], c1_alloc[1]) > max(c2_alloc[0], c2_alloc[1])
        c2_wins = max(c2_alloc[0], c2_alloc[1]) > max(c1_alloc[0], c1_alloc[1])
        return (f"s{c1_wins}-{c2_wins}", c1_wins + int(c1_wins), c2_wins + int(c2_wins))

    def _determine_outcome(self, joint_action):
        c1_alloc, c2_alloc = joint_action
        c1_wins = max(c1_alloc[0], c1_alloc[1]) > max(c2_alloc[0], c2_alloc[1])
        c2_wins = max(c2_alloc[0], c2_alloc[1]) > max(c1_alloc[0], c1_alloc[1])
        return (c1_wins, c2_wins)